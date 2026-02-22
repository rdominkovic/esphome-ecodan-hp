#include "asgard_dashboard.h"
#include "dashboard_html.h"
#include "dashboard_js.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"
#include <esp_http_server.h>
#include <cstdio>
#include <cstring>
#include <cmath>

// #include "esp_system.h"
// #include "esp_heap_caps.h"

namespace esphome {
namespace asgard_dashboard {

static const char *const TAG = "asgard_dashboard";

void EcodanDashboard::setup() {
  ESP_LOGI(TAG, "Setting up Ecodan Dashboard on /dashboard");
  base_->init();
  base_->add_handler(this);
}

void EcodanDashboard::loop() {

  uint32_t now = millis();
  if (now - last_history_time_ >= 60000 || last_history_time_ == 0) {
    last_history_time_ = now;
    record_history_();
  }

  if (action_queue_.empty()) return;

  std::vector<DashboardAction> todo;
  {
    std::lock_guard<std::mutex> lock(action_lock_);
    todo = action_queue_;
    action_queue_.clear();
  }

  for (const auto &act : todo) {
    this->dispatch_set_(act.key, act.s_value, act.f_value, act.is_string);
  }
}

bool EcodanDashboard::canHandle(AsyncWebServerRequest *request) const {
  const auto& url = request->url();
  return (url == "/dashboard" || url == "/dashboard/" ||
          url == "/dashboard/state" || url == "/dashboard/set" ||
          url == "/dashboard/history" ||
          url == "/js/chart.js" || url == "/js/hammer.js" || url == "/js/zoom.js"); 
}

void EcodanDashboard::handleRequest(AsyncWebServerRequest *request) {
  const auto& url = request->url();
  
  if      (url == "/dashboard" || url == "/dashboard/") handle_root_(request);
  else if (url == "/dashboard/state")                   handle_state_(request);
  else if (url == "/dashboard/set")                     handle_set_(request);
  else if (url == "/dashboard/history")                 handle_history_request_(request);
  else if (url == "/js/chart.js" || url == "/js/hammer.js" || url == "/js/zoom.js") {
    handle_js_(request);
  }
  else {
    request->send(404, "text/plain", "Not found");
  }
}

void EcodanDashboard::send_chunked_(AsyncWebServerRequest *request, const char *content_type, const uint8_t *data, size_t length, const char *cache_control) {
  // Extract the native ESP-IDF request pointer
  httpd_req_t *req = *request;
  httpd_resp_set_status(req, "200 OK");
  httpd_resp_set_type(req, content_type);
  httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
  
  if (cache_control != nullptr) {
    httpd_resp_set_hdr(req, "Cache-Control", cache_control);
  }

  // Send the compressed array in safe chunks
  size_t index = 0;
  size_t remaining = length;
  const size_t chunk_size = 2048;

  while (remaining > 0) {
    size_t to_send = (remaining < chunk_size) ? remaining : chunk_size;
    
    httpd_resp_send_chunk(req, (const char*)(data + index), to_send);
    
    index += to_send;
    remaining -= to_send;
  }

  httpd_resp_send_chunk(req, nullptr, 0);
}

void EcodanDashboard::handle_root_(AsyncWebServerRequest *request) {
  // uint32_t free_heap = esp_get_free_heap_size();
  // uint32_t max_block = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
  // ESP_LOGI(TAG, "handle_root_: Memory Stats | Total Free: %u bytes | Largest Block: %u bytes", free_heap, max_block);
  send_chunked_(request, "text/html", DASHBOARD_HTML_GZ, DASHBOARD_HTML_GZ_LEN, "no-cache");
}

void EcodanDashboard::handle_js_(AsyncWebServerRequest *request) {
  // uint32_t free_heap = esp_get_free_heap_size();
  // uint32_t max_block = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
  // ESP_LOGI(TAG, "handle_js_: Memory Stats | Total Free: %u bytes | Largest Block: %u bytes", free_heap, max_block);

  const auto& url = request->url();
  const uint8_t *file_data = nullptr;
  size_t file_len = 0;

  // Determine which file to serve
  if (url == "/js/chart.js") {
    file_data = CHARTJS_GZ;
    file_len = CHARTJS_GZ_LEN;
  } else if (url == "/js/hammer.js") {
    file_data = HAMMERJS_GZ;
    file_len = HAMMERJS_GZ_LEN;
  } else if (url == "/js/zoom.js") {
    file_data = ZOOMJS_GZ;
    file_len = ZOOMJS_GZ_LEN;
  } else {
    request->send(404, "text/plain", "File not found");
    return;
  }

  send_chunked_(request, "application/javascript", file_data, file_len, "public, max-age=31536000");
}

void EcodanDashboard::handle_state_(AsyncWebServerRequest *request) {
  // uint32_t free_heap = esp_get_free_heap_size();
  // uint32_t max_block = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
  // ESP_LOGI(TAG, "handle_state_: Memory Stats | Total Free: %u bytes | Largest Block: %u bytes", free_heap, max_block);

  httpd_req_t *req = *request;
  httpd_resp_set_status(req, "200 OK");
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache");

  httpd_resp_send_chunk(req, "{", 1);

  char shared_buf[128];

  // --- ZERO-ALLOCATION HELPER LAMBDAS ---
  auto p_sens = [&](const char* k, sensor::Sensor* s) {
    int len = (s && s->has_state() && !std::isnan(s->state)) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":%.2f,", k, s->state)
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };
  
  auto p_num = [&](const char* k, number::Number* n) {
    int len = (n && n->has_state() && !std::isnan(n->state)) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":%.1f,", k, n->state)
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_lim = [&](const char* k, number::Number* n) {
    int len = (n) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":{\"min\":%.1f,\"max\":%.1f,\"step\":%.1f},", 
                         k, n->traits.get_min_value(), n->traits.get_max_value(), n->traits.get_step())
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_bin = [&](const char* k, binary_sensor::BinarySensor* b) {
    int len = (b && b->has_state()) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":%s,", k, b->state ? "true" : "false")
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_sw = [&](const char* k, switch_::Switch* sw) {
    int len = (sw) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":%s,", k, sw->state ? "true" : "false")
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_sel = [&](const char* k, select::Select* sel) {
    int len = 0;
    if (sel) {
      auto opt_index = sel->active_index(); 
      if (opt_index.has_value()) {
        len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"%zu\",", k, opt_index.value());
        httpd_resp_send_chunk(req, shared_buf, len);
        return;
      }
    }
    len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_txt = [&](const char* k, text_sensor::TextSensor* t) {
    int len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"", k);
    httpd_resp_send_chunk(req, shared_buf, len);
    
    if (t && t->has_state()) {
      // Safe string escaping directly from the state
      strncpy(shared_buf, t->state.c_str(), sizeof(shared_buf) - 1);
      shared_buf[sizeof(shared_buf) - 1] = '\0'; 
      
      for (char *c = shared_buf; *c != '\0'; ++c) {
        if (*c == '"') httpd_resp_send_chunk(req, "\\\"", 2);
        else if (*c == '\\') httpd_resp_send_chunk(req, "\\\\", 2);
        else httpd_resp_send_chunk(req, c, 1);
      }
    }
    httpd_resp_send_chunk(req, "\",", 2);
  };

  auto p_clim_cur = [&](const char* k, climate::Climate* c) {
    int len = (c && !std::isnan(c->current_temperature)) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":%.1f,", k, c->current_temperature)
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_clim_tar = [&](const char* k, climate::Climate* c) {
    int len = (c && !std::isnan(c->target_temperature)) 
              ? snprintf(shared_buf, sizeof(shared_buf), "\"%s\":%.1f,", k, c->target_temperature)
              : snprintf(shared_buf, sizeof(shared_buf), "\"%s\":null,", k);
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_clim_act = [&](const char* k, climate::Climate* c) {
    int len;
    if (!c) { len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"off\",", k); }
    else {
      switch (c->action) {
        case climate::CLIMATE_ACTION_OFF:     len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"off\",", k); break;
        case climate::CLIMATE_ACTION_COOLING: len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"cooling\",", k); break;
        case climate::CLIMATE_ACTION_HEATING: len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"heating\",", k); break;
        case climate::CLIMATE_ACTION_DRYING:  len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"drying\",", k); break;
        case climate::CLIMATE_ACTION_IDLE: 
        default:                              len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"idle\",", k); break;
      }
    }
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  auto p_clim_mode = [&](const char* k, climate::Climate* c) {
    int len;
    if (!c) { len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"off\",", k); }
    else {
      switch (c->mode) {
        case climate::CLIMATE_MODE_HEAT: len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"heat\",", k); break;
        case climate::CLIMATE_MODE_COOL: len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"cool\",", k); break;
        case climate::CLIMATE_MODE_AUTO: len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"auto\",", k); break;
        case climate::CLIMATE_MODE_OFF:
        default:                         len = snprintf(shared_buf, sizeof(shared_buf), "\"%s\":\"off\",", k); break;
      }
    }
    httpd_resp_send_chunk(req, shared_buf, len);
  };

  // stream data
  int t_len = snprintf(shared_buf, sizeof(shared_buf), "\"ui_use_room_z1\":%s,", (ui_use_room_z1_ != nullptr) && ui_use_room_z1_->value() ? "true" : "false");
  httpd_resp_send_chunk(req, shared_buf, t_len);
  
  t_len = snprintf(shared_buf, sizeof(shared_buf), "\"ui_use_room_z2\":%s,", (ui_use_room_z2_ != nullptr) && ui_use_room_z2_->value() ? "true" : "false");
  httpd_resp_send_chunk(req, shared_buf, t_len);
  
  p_sens("hp_feed_temp", hp_feed_temp_);
  p_sens("hp_return_temp", hp_return_temp_);
  p_sens("outside_temp", outside_temp_);
  p_sens("compressor_frequency", compressor_frequency_);
  p_sens("flow_rate", flow_rate_);
  p_sens("computed_output_power", computed_output_power_);
  p_sens("daily_computed_output_power", daily_computed_output_power_);
  p_sens("daily_total_energy_consumption", daily_total_energy_consumption_);
  p_sens("compressor_starts", compressor_starts_);
  p_sens("runtime", runtime_);
  p_sens("wifi_signal_db", wifi_signal_db_);

  p_sens("dhw_temp", dhw_temp_);
  p_sens("dhw_flow_temp_target", dhw_flow_temp_target_);
  p_sens("dhw_flow_temp_drop", dhw_flow_temp_drop_);
  p_sens("dhw_consumed", dhw_consumed_);
  p_sens("dhw_delivered", dhw_delivered_);
  p_sens("dhw_cop", dhw_cop_);

  p_sens("heating_consumed", heating_consumed_);
  p_sens("heating_produced", heating_produced_);
  p_sens("heating_cop", heating_cop_);
  p_sens("cooling_consumed", cooling_consumed_);
  p_sens("cooling_produced", cooling_produced_);
  p_sens("cooling_cop", cooling_cop_);

  p_sens("z1_flow_temp_target", z1_flow_temp_target_);
  p_sens("z2_flow_temp_target", z2_flow_temp_target_);

  p_num("auto_adaptive_setpoint_bias", num_aa_setpoint_bias_);
  p_lim("aa_bias_lim", num_aa_setpoint_bias_);
  
  p_num("maximum_heating_flow_temp", num_max_flow_temp_);
  p_lim("max_flow_lim", num_max_flow_temp_);
  p_num("minimum_heating_flow_temp", num_min_flow_temp_);
  p_lim("min_flow_lim", num_min_flow_temp_);

  p_num("maximum_heating_flow_temp_z2", num_max_flow_temp_z2_);
  p_lim("max_flow_z2_lim", num_max_flow_temp_z2_);
  p_num("minimum_heating_flow_temp_z2", num_min_flow_temp_z2_);
  p_lim("min_flow_z2_lim", num_min_flow_temp_z2_);

  p_num("thermostat_hysteresis_z1", num_hysteresis_z1_);
  p_lim("hysteresis_z1_lim", num_hysteresis_z1_);
  
  p_num("thermostat_hysteresis_z2", num_hysteresis_z2_);
  p_lim("hysteresis_z2_lim", num_hysteresis_z2_);

  p_num("pred_sc_time", pred_sc_time_);
  p_lim("pred_sc_time_lim", pred_sc_time_);
  p_num("pred_sc_delta", pred_sc_delta_);
  p_lim("pred_sc_delta_lim", pred_sc_delta_);  

  p_clim_cur("z1_current_temp", virtual_climate_z1_);
  p_clim_tar("z1_setpoint", virtual_climate_z1_);
  p_clim_act("z1_action", virtual_climate_z1_);
  p_clim_mode("z1_mode", virtual_climate_z1_);

  p_clim_cur("z2_current_temp", virtual_climate_z2_);
  p_clim_tar("z2_setpoint", virtual_climate_z2_);
  p_clim_act("z2_action", virtual_climate_z2_);
  p_clim_mode("z2_mode", virtual_climate_z2_);

  p_clim_cur("room_z1_current", heatpump_climate_z1_);
  p_clim_tar("room_z1_setpoint", heatpump_climate_z1_);
  p_clim_act("room_z1_action", heatpump_climate_z1_);

  p_clim_cur("room_z2_current", heatpump_climate_z2_);
  p_clim_tar("room_z2_setpoint", heatpump_climate_z2_);
  p_clim_act("room_z2_action", heatpump_climate_z2_);

  p_clim_cur("flow_z1_current", flow_climate_z1_);
  p_clim_tar("flow_z1_setpoint", flow_climate_z1_);
  p_clim_cur("flow_z2_current", flow_climate_z2_);
  p_clim_tar("flow_z2_setpoint", flow_climate_z2_);

  p_bin("status_compressor", status_compressor_);
  p_bin("status_booster", status_booster_);
  p_bin("status_defrost", status_defrost_);
  p_bin("status_water_pump", status_water_pump_);
  p_bin("status_in1_request", status_in1_request_);
  p_bin("status_in6_request", status_in6_request_);
  
  t_len = snprintf(shared_buf, sizeof(shared_buf), "\"zone2_enabled\":%s,", bin_state_(status_zone2_enabled_) ? "true" : "false");
  httpd_resp_send_chunk(req, shared_buf, t_len);

  p_sw("pred_sc_en", pred_sc_switch_);
  p_sw("auto_adaptive_control_enabled", sw_auto_adaptive_);
  p_sw("defrost_risk_handling_enabled", sw_defrost_mit_);
  p_sw("smart_boost_enabled", sw_smart_boost_);
  p_sw("force_dhw", sw_force_dhw_); 
  
  p_txt("latest_version", version_);

  if (operation_mode_ && operation_mode_->has_state() && !std::isnan(operation_mode_->state)) {
    t_len = snprintf(shared_buf, sizeof(shared_buf), "\"operation_mode\":%d,", (int)operation_mode_->state);
  } else {
    t_len = snprintf(shared_buf, sizeof(shared_buf), "\"operation_mode\":null,");
  }
  httpd_resp_send_chunk(req, shared_buf, t_len);
  
  p_sel("heating_system_type", sel_heating_system_type_);
  p_sel("room_temp_source_z1", sel_room_temp_source_z1_);
  p_sel("room_temp_source_z2", sel_room_temp_source_z2_);
  p_sel("operating_mode_z1", sel_operating_mode_z1_);
  p_sel("operating_mode_z2", sel_operating_mode_z2_);
  p_sel("temp_sensor_source_z1", sel_temp_source_z1_);
  p_sel("temp_sensor_source_z2", sel_temp_source_z2_);

  t_len = snprintf(shared_buf, sizeof(shared_buf), "\"_uptime_ms\":%u}", millis());
  httpd_resp_send_chunk(req, shared_buf, t_len);
  
  // Send 0-length chunk to complete the transfer
  httpd_resp_send_chunk(req, nullptr, 0);
}

void EcodanDashboard::handle_set_(AsyncWebServerRequest *request) {
  if (request->method() != HTTP_POST) {
    request->send(405, "text/plain", "Method Not Allowed");
    return;
  }

  httpd_req_t *req = *request;
  size_t content_len = req->content_len;
  if (content_len == 0 || content_len > 512) {
    request->send(400, "text/plain", "Bad Request");
    return;
  }

  char body[513] = {0};
  int received = httpd_req_recv(req, body, content_len);
  if (received <= 0) {
    request->send(400, "text/plain", "Read failed");
    return;
  }
  body[received] = '\0';

  ESP_LOGI(TAG, "Dashboard POST body: %s", body);

  char key[64] = {0};
  const char *kp = strstr(body, "\"key\":");
  if (kp) {
    kp += 6;
    while (*kp == ' ' || *kp == '"') kp++;
    int i = 0;
    while (*kp && *kp != '"' && i < 63) key[i++] = *kp++;
  }
  if (strlen(key) == 0) { request->send(400, "text/plain", "Missing key"); return; }

  char strval[128] = {0};
  float fval = 0.0f;
  bool is_string = false;

  const char *vp = strstr(body, "\"value\":");
  if (vp) {
    vp += 8;
    while (*vp == ' ') vp++;
    if (*vp == '"') {
      is_string = true;
      vp++;
      int i = 0;
      while (*vp && *vp != '"' && i < 127) strval[i++] = *vp++;
    } else {
      fval = static_cast<float>(atof(vp));
    }
  }

  ESP_LOGI(TAG, "Dashboard set: key=%s value=%s/%.2f", key,
           is_string ? strval : "-", is_string ? 0.0f : fval);

  {
    std::lock_guard<std::mutex> lock(action_lock_);
    action_queue_.push_back({
        std::string(key),
        std::string(strval),
        fval,
        is_string
    });
  }

  request->send(200, "application/json", "{\"ok\":true}");
}

void EcodanDashboard::dispatch_set_(const std::string &key, const std::string &sval, float fval, bool is_string) {
  auto doSwitch = [&](switch_::Switch *sw) {
    if (!sw) { ESP_LOGW(TAG, "Switch not configured"); return; }
    fval > 0.5f ? sw->turn_on() : sw->turn_off();
  };
  if (key == "auto_adaptive_control_enabled") { doSwitch(sw_auto_adaptive_); return; }
  if (key == "defrost_risk_handling_enabled") { doSwitch(sw_defrost_mit_);   return; }
  if (key == "smart_boost_enabled")           { doSwitch(sw_smart_boost_);   return; }
  if (key == "force_dhw")                     { doSwitch(sw_force_dhw_);     return; } 
  if (key == "predictive_short_cycle_control_enabled") { doSwitch(pred_sc_switch_);   return; }

  auto doSelect = [&](select::Select *sel) {
    if (!sel) { ESP_LOGW(TAG, "Select not configured"); return; }
    auto call = sel->make_call();
    if (is_string) {
      call.set_option(sval);
    } else {
      call.set_index((size_t)fval);
    }
    call.perform();
  };

  if (key == "heating_system_type")   { doSelect(sel_heating_system_type_); return; }
  if (key == "room_temp_source_z1")   { doSelect(sel_room_temp_source_z1_); return; }
  if (key == "room_temp_source_z2")   { doSelect(sel_room_temp_source_z2_); return; }
  if (key == "operating_mode_z1")     { doSelect(sel_operating_mode_z1_); return; }
  if (key == "operating_mode_z2")     { doSelect(sel_operating_mode_z2_); return; }
  if (key == "temp_sensor_source_z1") { doSelect(sel_temp_source_z1_); return; } 
  if (key == "temp_sensor_source_z2") { doSelect(sel_temp_source_z2_); return; } 

  auto doNumber = [&](number::Number *n) {
    if (!n) { ESP_LOGW(TAG, "Number not configured"); return; }
    auto call = n->make_call();
    call.set_value(fval);
    call.perform();
  };
  if (key == "auto_adaptive_setpoint_bias") { doNumber(num_aa_setpoint_bias_); return; }
  if (key == "maximum_heating_flow_temp")   { doNumber(num_max_flow_temp_);    return; }
  if (key == "minimum_heating_flow_temp")   { doNumber(num_min_flow_temp_);    return; }
  if (key == "maximum_heating_flow_temp_z2") { doNumber(num_max_flow_temp_z2_); return; }
  if (key == "minimum_heating_flow_temp_z2") { doNumber(num_min_flow_temp_z2_); return; }
  if (key == "thermostat_hysteresis_z1")    { doNumber(num_hysteresis_z1_);    return; }
  if (key == "thermostat_hysteresis_z2")    { doNumber(num_hysteresis_z2_);    return; }

  if (key == "predictive_short_cycle_high_delta_time_window")    { doNumber(pred_sc_time_);    return; }
  if (key == "predictive_short_cycle_high_delta_threshold")    { doNumber(pred_sc_delta_);    return; }

  if (key == "dhw_setpoint" && dhw_climate_ != nullptr) {
    auto call = dhw_climate_->make_call();
    call.set_target_temperature(fval);
    call.perform();
    ESP_LOGI(TAG, "DHW setpoint: %.1f", fval);
    return;
  }

  auto doClimate = [&](climate::Climate *c, const char *name) {
    if (!c) { ESP_LOGW(TAG, "%s climate not configured", name); return; }
    auto call = c->make_call();
    call.set_target_temperature(fval);
    call.perform();
    ESP_LOGI(TAG, "%s setpoint: %.1f", name, fval);
  };
  if (key == "virtual_climate_z1_setpoint") { doClimate(virtual_climate_z1_, "Z1"); return; }
  if (key == "virtual_climate_z2_setpoint") { doClimate(virtual_climate_z2_, "Z2"); return; }

  if (key == "heatpump_climate_z1_setpoint") { doClimate(heatpump_climate_z1_, "Room Z1"); return; }
  if (key == "heatpump_climate_z2_setpoint") { doClimate(heatpump_climate_z2_, "Room Z2"); return; }

  if (key == "flow_climate_z1_setpoint")     { doClimate(flow_climate_z1_, "Flow Z1"); return; }
  if (key == "flow_climate_z2_setpoint")     { doClimate(flow_climate_z2_, "Flow Z2"); return; }
  
  if (key == "virtual_climate_z1_mode" || key == "virtual_climate_z2_mode") {
    climate::Climate *c = (key == "virtual_climate_z1_mode") ? virtual_climate_z1_ : virtual_climate_z2_;
    if (c && is_string) {
      auto call = c->make_call();
      if (sval == "heat") call.set_mode(climate::CLIMATE_MODE_HEAT);
      else if (sval == "cool") call.set_mode(climate::CLIMATE_MODE_COOL);
      else if (sval == "auto") call.set_mode(climate::CLIMATE_MODE_AUTO);
      else call.set_mode(climate::CLIMATE_MODE_OFF);
      call.perform();
      ESP_LOGI(TAG, "%s set to %s", key.c_str(), sval.c_str());
    }
    return;
  }

  if (key == "ui_use_room_z1" && ui_use_room_z1_) { ui_use_room_z1_->value() = (fval > 0.5); return; }
  if (key == "ui_use_room_z2" && ui_use_room_z2_) { ui_use_room_z2_->value() = (fval > 0.5); return; }

  if (is_string) {
     ESP_LOGW(TAG, "Unknown string key: %s", key.c_str());
  }
}

// History handling
int16_t EcodanDashboard::pack_temp_(float val) {
  if (std::isnan(val)) return -32768; 
  return static_cast<int16_t>(val * 10.0f);
}

bool EcodanDashboard::bin_state_(binary_sensor::BinarySensor *b) {
  return (b != nullptr && b->has_state() && b->state);
}

void EcodanDashboard::record_history_() {
  HistoryRecord rec;
  rec.timestamp = time(nullptr); 

  auto get_sensor = [](sensor::Sensor *s) { return (s && s->has_state()) ? s->state : NAN; };
  auto get_curr = [](climate::Climate *c) { return (c) ? c->current_temperature : NAN; };
  auto get_targ = [](climate::Climate *c) { return (c) ? c->target_temperature : NAN; };

  rec.hp_feed   = pack_temp_(get_sensor(hp_feed_temp_));
  rec.hp_return = pack_temp_(get_sensor(hp_return_temp_));
  rec.z1_sp     = pack_temp_(get_targ(virtual_climate_z1_));
  rec.z2_sp     = pack_temp_(get_targ(virtual_climate_z2_));
  rec.z1_curr   = pack_temp_(get_curr(virtual_climate_z1_));
  rec.z2_curr   = pack_temp_(get_curr(virtual_climate_z2_));
  rec.z1_flow   = pack_temp_(get_sensor(z1_flow_temp_target_));
  rec.z2_flow   = pack_temp_(get_sensor(z2_flow_temp_target_));
  rec.freq      = pack_temp_(get_sensor(compressor_frequency_));

  rec.flags = 0;
  if (bin_state_(status_compressor_))  rec.flags |= (1 << 0);
  if (bin_state_(status_booster_))     rec.flags |= (1 << 1);
  if (bin_state_(status_defrost_))     rec.flags |= (1 << 2);
  if (bin_state_(status_water_pump_))  rec.flags |= (1 << 3);
  if (bin_state_(status_in1_request_)) rec.flags |= (1 << 4);
  if (bin_state_(status_in6_request_)) rec.flags |= (1 << 5);

  uint8_t mode_enc = 0; // Default to OFF
  if (operation_mode_ && operation_mode_->has_state() && !std::isnan(operation_mode_->state)) {
    int val = (int)operation_mode_->state;
    if (val != 255) mode_enc = val & 0x0F; // enum value
  }
  rec.flags |= ((mode_enc & 0x0F) << 6);

  history_buffer_[history_head_] = rec;
  history_head_ = (history_head_ + 1) % MAX_HISTORY;
  if (history_count_ < MAX_HISTORY) history_count_++;
}

void EcodanDashboard::handle_history_request_(AsyncWebServerRequest *request) {
  httpd_req_t *req = *request;
  httpd_resp_set_status(req, "200 OK");
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache");

  size_t current_count = history_count_;
  size_t current_head = history_head_;

  if (current_count == 0) {
    httpd_resp_send_chunk(req, "[]", 2);
    httpd_resp_send_chunk(req, nullptr, 0); 
    return;
  }
  
  size_t start_idx = (current_count == MAX_HISTORY) ? current_head : 0;
  size_t step = (current_count > 360) ? (current_count / 360) : 1;
  if (step < 1) step = 1;
  
  // Start the JSON array
  httpd_resp_send_chunk(req, "[", 1);
  
  bool first = true;
  for (size_t i = 0; i < current_count; i += step) {
    size_t idx = (start_idx + i) % MAX_HISTORY;
    HistoryRecord rec = history_buffer_[idx];
    
    if (!first) {
      httpd_resp_send_chunk(req, ",", 1);
    }
    first = false;
    
    char item[128];
    int len = snprintf(item, sizeof(item), "[%u,%d,%d,%d,%d,%d,%d,%d,%d,%d,%u]", 
      rec.timestamp, rec.hp_feed, rec.hp_return, 
      rec.z1_sp, rec.z2_sp, rec.z1_curr, rec.z2_curr, 
      rec.z1_flow, rec.z2_flow, rec.freq, rec.flags
    );
    httpd_resp_send_chunk(req, item, len);
  }
  httpd_resp_send_chunk(req, "]", 1);
  // Send 0-length chunk to signal the end of the transmission
  httpd_resp_send_chunk(req, nullptr, 0);
}

}  // namespace asgard_dashboard
}  // namespace esphome