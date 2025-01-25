pilot_execution:
  initial_validation:
    pre_flight_checks:
      backup_verification:
        - check: "backup_system_operational"
          status: "required"
          validation: "async_backup_test"
        - check: "state_persistence_ready"
          status: "required"
          validation: "s3_bucket_test"
        - check: "monitoring_systems_active"
          status: "required"
          validation: "metric_stream_test"
      
      target_workload:
        name: "nightly_etl_batch"
        current_state:
          - metric: "average_completion_time"
            value: "baseline_capture"
          - metric: "resource_utilization"
            value: "baseline_capture"
          - metric: "error_rate"
            value: "baseline_capture"
        
      failover_readiness:
        - check: "ondemand_capacity_reserved"
          status: "required"
          validation: "capacity_reservation_test"
        - check: "failback_automation_ready"
          status: "required"
          validation: "automation_test"

  staged_migration:
    phase_1_preparation:
      duration: "30m"
      steps:
        - action: "create_spot_fleet_request"
          config:
            instance_types: ["m5.large", "m5a.large", "m5n.large"]
            strategy: "capacity-optimized"
            allocation_strategy: "price-capacity-optimized"
            target_capacity: 1
            max_price: "on-demand-price * 0.7"
        
        - action: "verify_spot_market"
          criteria:
            - condition: "spot_price_stability"
              threshold: "< 20% variation past 24h"
            - condition: "interruption_rate"
              threshold: "< 5% past 24h"

    phase_2_pilot_launch:
      duration: "2h"
      steps:
        - action: "launch_shadow_mode"
          config:
            - parallel_processing: true
            - compare_outputs: true
            - error_threshold: 0
        
        - action: "validate_performance"
          criteria:
            - metric: "processing_time"
              threshold: "baseline + 5%"
            - metric: "error_rate"
              threshold: "0%"
            - metric: "resource_efficiency"
              threshold: ">= baseline"

    phase_3_cutover:
      duration: "1h"
      steps:
        - action: "gradual_traffic_shift"
          config:
            - increment: 25
            - interval: "15m"
            - validation_period: "10m"
        
        - action: "performance_validation"
          criteria:
            - metric: "job_success_rate"
              threshold: "100%"
            - metric: "processing_time"
              threshold: "<= baseline + 5%"

  continuous_monitoring:
    critical_metrics:
      performance:
        - metric: "job_completion_time"
          threshold: "baseline + 5%"
          window: "5m"
          action: "alert_and_investigate"
        
        - metric: "error_rate"
          threshold: "0.01%"
          window: "5m"
          action: "immediate_rollback"
        
        - metric: "resource_utilization"
          threshold: "80%"
          window: "5m"
          action: "scale_review"

      cost_efficiency:
        - metric: "cost_per_job"
          threshold: "< 50% of baseline"
          window: "1h"
          action: "optimization_review"
        
        - metric: "spot_savings"
          threshold: "> 60%"
          window: "1h"
          action: "strategy_validation"

    automated_responses:
      interruption_handling:
        - trigger: "spot_interruption_warning"
          actions:
            - "checkpoint_state"
            - "launch_replacement"
            - "validate_state"
          timing: "immediate"
        
        - trigger: "performance_degradation"
          actions:
            - "investigate_cause"
            - "prepare_failback"
            - "alert_team"
          timing: "within_1m"

  rollback_readiness:
    triggers:
      immediate:
        - condition: "error_rate > 0.01%"
          window: "1m"
        - condition: "job_failure"
          window: "immediate"
        - condition: "data_inconsistency"
          window: "immediate"
      
      gradual:
        - condition: "performance_degradation > 10%"
          window: "15m"
        - condition: "cost_efficiency < 40%"
          window: "1h"

    procedures:
      automated:
        - step: "pause_spot_fleet"
          timing: "immediate"
        - step: "activate_ondemand"
          timing: "within_30s"
        - step: "verify_stability"
          timing: "within_2m"
        - step: "restore_state"
          timing: "within_5m"