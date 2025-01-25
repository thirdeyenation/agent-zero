monitoring_framework:
  baseline_metrics:
    performance:
      system_health:
        - metric: "cpu_utilization"
          threshold: 80
          window: "5m"
          action: "alert"
        - metric: "memory_utilization"
          threshold: 85
          window: "5m"
          action: "alert"
        - metric: "disk_utilization"
          threshold: 75
          window: "15m"
          action: "alert"
      
      application_health:
        - metric: "error_rate"
          threshold: 0.1  # 0.1% error rate
          window: "5m"
          action: "rollback"
        - metric: "response_time_p95"
          threshold: 500  # milliseconds
          window: "5m"
          action: "alert"
        - metric: "request_success_rate"
          threshold: 99.9
          window: "5m"
          action: "rollback"

    business_metrics:
      - metric: "transaction_success_rate"
        threshold: 99.99
        window: "5m"
        action: "rollback"
      - metric: "order_processing_time"
        threshold: 2000  # milliseconds
        window: "5m"
        action: "alert"
      - metric: "customer_facing_errors"
        threshold: 0
        window: "5m"
        action: "rollback"

  automated_response:
    rollback_triggers:
      immediate:
        - condition: "error_rate > 0.1%"
          action: "immediate_rollback"
        - condition: "success_rate < 99.9%"
          action: "immediate_rollback"
        - condition: "customer_facing_errors > 0"
          action: "immediate_rollback"
      
      gradual:
        - condition: "response_time_increase > 20%"
          action: "investigate_and_plan_rollback"
        - condition: "resource_usage_spike > 30%"
          action: "investigate_and_plan_rollback"

    alert_triggers:
      warning:
        - condition: "resource_usage > 70%"
          action: "notify_team"
        - condition: "response_time_increase > 10%"
          action: "notify_team"
      
      critical:
        - condition: "resource_usage > 85%"
          action: "notify_team_and_escalate"
        - condition: "error_rate > 0.05%"
          action: "notify_team_and_escalate"

  validation_framework:
    pre_change:
      - baseline_collection:
          duration: "1h"
          metrics: "all_critical_metrics"
      - capacity_verification:
          check: "sufficient_headroom"
          threshold: "30%"
      - dependency_check:
          scope: "all_connected_services"
          depth: 2

    during_change:
      - real_time_comparison:
          baseline: "pre_change_metrics"
          window: "rolling_5m"
      - canary_metrics:
          sample_rate: 10
          duration: "15m"
      - rollback_readiness:
          verification: "continuous"

    post_change:
      - stability_verification:
          duration: "1h"
          comparison: "baseline"
      - performance_validation:
          metrics: "all_critical_metrics"
          threshold: "5%_deviation"
      - user_impact_analysis:
          metrics: "customer_facing_metrics"
          threshold: "0_impact"

  cost_tracking:
    resource_metrics:
      - metric: "cost_per_request"
        threshold: "current_baseline * 1.1"
        window: "1h"
      - metric: "resource_cost_per_service"
        threshold: "current_baseline * 1.15"
        window: "1h"
    
    optimization_metrics:
      - metric: "cost_reduction_percentage"
        target: "minimum_20_percent"
        window: "24h"
      - metric: "resource_efficiency_score"
        target: "minimum_85_percent"
        window: "1h"