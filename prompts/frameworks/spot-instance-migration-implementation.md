spot_migration_execution:
  stage_1_preparation:
    workload_identification:
      batch_processing:
        criteria:
          - interruption_tolerant: true
          - stateless_preferred: true
          - no_real_time_requirements: true
        target_services:
          - name: "data_etl_jobs"
            current_instance: "m5.large"
            spot_target: "m5.large, m5a.large, m5n.large"
            fallback: "m5.large"
          - name: "report_generation"
            current_instance: "c5.xlarge"
            spot_target: "c5.xlarge, c5a.xlarge, c5n.xlarge"
            fallback: "c5.xlarge"

    safety_configuration:
      instance_termination_handling:
        - checkpointing_interval: "5m"
        - graceful_shutdown_time: "120s"
        - state_persistence_path: "s3://backup-bucket/spot-state/"
        
      failover_configuration:
        primary:
          - region: "us-east-1"
            az_preference: ["us-east-1a", "us-east-1b", "us-east-1c"]
        backup:
          - region: "us-east-2"
            az_preference: ["us-east-2a", "us-east-2b"]

  stage_2_pilot_migration:
    initial_service:
      name: "nightly_etl_batch"
      implementation:
        - step: "Create spot fleet request"
          config:
            instance_types: ["m5.large", "m5a.large", "m5n.large"]
            max_price: "on-demand-price * 0.7"
            capacity: 1
            strategy: "capacity-optimized"
            
        - step: "Configure AutoScaling"
          config:
            min_capacity: 1
            max_capacity: 2
            target_capacity: 1
            scale_up_threshold: "CPU > 75% for 10m"
            scale_down_threshold: "CPU < 30% for 20m"

        - step: "Setup monitoring"
          config:
            metrics:
              - spot_instance_interruption
              - job_completion_rate
              - processing_time
              - cost_per_job
            alerts:
              - interruption_prediction
              - performance_degradation
              - cost_anomaly

    validation_period:
      duration: "48h"
      success_criteria:
        - metric: "job_completion_rate"
          threshold: ">= 99.9%"
        - metric: "processing_time"
          threshold: "<= baseline + 10%"
        - metric: "cost_savings"
          threshold: ">= 50%"

  stage_3_expansion:
    rollout_plan:
      phase_1:
        services:
          - "report_generation"
          - "data_analytics"
        duration: "1 week"
        validation: "72h per service"

      phase_2:
        services:
          - "log_processing"
          - "backup_jobs"
        duration: "1 week"
        validation: "72h per service"

    automation_implementation:
      spot_fleet_management:
        - automatic_bidding:
            max_bid: "on-demand-price * 0.8"
            bid_adjustment_interval: "5m"
        - capacity_management:
            rebalancing_strategy: "proactive"
            replacement_delay: "120s"
        - interruption_handling:
            advance_notice: "120s"
            checkpointing: "enabled"
            state_backup: "enabled"

  monitoring_and_optimization:
    metrics_tracking:
      cost_efficiency:
        - savings_per_service
        - total_cost_reduction
        - spot_vs_ondemand_ratio
        - interruption_impact
      
      performance:
        - job_completion_times
        - processing_throughput
        - error_rates
        - recovery_times
      
      reliability:
        - interruption_frequency
        - successful_migrations
        - failed_migrations
        - recovery_success_rate

    continuous_optimization:
      automated_adjustments:
        - bid_price_optimization:
            frequency: "hourly"
            strategy: "market_based"
        - instance_type_selection:
            frequency: "daily"
            strategy: "performance_cost_balanced"
        - capacity_planning:
            frequency: "weekly"
            strategy: "usage_pattern_based"