# Data Directory Structure

## Experiments
The `experiments/` directory provides two complementary views of the data:

```
experiments/
├── users/                # User-centric view
│   └── USER_ID/         # Individual user directory (e.g., 31499533)
│       └── RUN_ID/      # Experiment run for this user
│           ├── batch.jsonl    # User's batch file
│           ├── upload.json    # Groq upload response
│           └── results.json   # User's results
│
└── runs/                # Run-centric view
    └── RUN_ID/         # Run identifier (format: YYYYMMDD_TYPE_MODEL_XXX)
        ├── config.yaml  # Shared configuration
        ├── users.json   # List of users {"users": ["31499533", ...]}
        └── status.json  # Run status tracking
```

### Key Features:
- Two complementary views of the data
- Clean user directories with just IDs
- Systematic run identifiers
- Run status tracking
- Simple, logical structure

### Example:
```
experiments/
├── users/
│   ├── 31499533/
│   │   └── 20240408_CT_DS70B_001/
│   │       ├── batch.jsonl
│   │       ├── upload.json
│   │       └── results.json
│   │
│   └── 31499534/
│       └── 20240408_CT_DS70B_001/
│           ├── batch.jsonl
│           ├── upload.json
│           └── results.json
│
└── runs/
    └── 20240408_CT_DS70B_001/        # April 8, 2024, Closed Target, Deepseek 70B, Run 001
        ├── config.yaml  # Shared configuration
        ├── users.json   # {"users": ["31499533", "31499534"]}
        └── status.json  # {
                        #   "created": "2024-04-08T10:30:00",
                        #   "steps": {
                        #     "config_created": true,
                        #     "batches_created": true,
                        #     "uploads_completed": true,
                        #     "results_received": false
                        #   },
                        #   "last_updated": "2024-04-08T11:45:00",
                        #   "description": "Closed target experiment with Deepseek 70B model"
                        # }
```

### Run Identifier Format
The run identifier follows the pattern: `YYYYMMDD_TYPE_MODEL_XXX`
- `YYYYMMDD`: Date of the run
- `TYPE`: Experiment type (e.g., CT=Closed Target, OT=Open Target)
- `MODEL`: Model identifier (e.g., DS70B=Deepseek 70B)
- `XXX`: Sequential number (001, 002, etc.)

Examples:
- `20240408_CT_DS70B_001`: Closed Target, Deepseek 70B, First run
- `20240408_OT_DS70B_001`: Open Target, Deepseek 70B, First run
- `20240408_CT_L70B_001`: Closed Target, Llama 70B, First run

This structure:
1. Provides both user and run perspectives
2. Makes it easy to find all experiments for a user
3. Makes it easy to find all users in a run
4. Uses systematic and sortable run identifiers
5. Tracks run status and progress
6. Maintains clean directory names
7. Provides clear experiment identification

Note: The legacy directories (`batch_files/` and `results/`) are deprecated in favor of this new structure. 