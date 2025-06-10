from dataclasses import dataclass, field
from typing import Optional, Literal, List


@dataclass
class LocalizationArgs:
    """Arguments for the script."""

    output_folder: str = field(metadata={"help": "Output folder."})
    output_file: str = field(default="loc_outputs.jsonl", metadata={"help": "Output file name."})
    start_file: Optional[str] = field(
        default=None,
        metadata={
            "help": "Previous output file to start with to reduce the work, should use in combination without --file_level."
        },
    )
    file_level: bool = field(
        default=False, metadata={"help": "Enable file level processing."}
    )
    related_level: bool = field(
        default=False, metadata={"help": "Enable related level processing."}
    )
    fine_grain_line_level: bool = field(
        default=False, metadata={"help": "Enable fine-grain line level processing."}
    )
    top_n: int = field(default=3, metadata={"help": "Top N results."})
    temperature: float = field(default=0.0, metadata={"help": "Sampling temperature."})
    num_samples: int = field(default=1, metadata={"help": "Number of samples."})
    compress: bool = field(default=False, metadata={"help": "Enable compression."})
    compress_assign: bool = field(
        default=False, metadata={"help": "Enable compression for assignments."}
    )
    compress_assign_total_lines: int = field(
        default=30, metadata={"help": "Total lines for compressed assignment."}
    )
    compress_assign_prefix_lines: int = field(
        default=10, metadata={"help": "Prefix lines for compressed assignment."}
    )
    compress_assign_suffix_lines: int = field(
        default=10, metadata={"help": "Suffix lines for compressed assignment."}
    )
    merge: bool = field(default=False, metadata={"help": "Enable merging."})
    add_space: bool = field(default=False, metadata={"help": "Add space."})
    no_line_number: bool = field(
        default=False, metadata={"help": "Disable line numbers."}
    )
    sticky_scroll: bool = field(
        default=False, metadata={"help": "Enable sticky scroll."}
    )
    related_level_separate_file: bool = field(
        default=False, metadata={"help": "Save related level to a separate file."}
    )
    context_window: int = field(
        default=10, metadata={"help": "Context window size."}
    )
    keep_old_order: bool = field(
        default=False, metadata={"help": "Keep old order of elements."}
    )
    irrelevant: bool = field(default=False, metadata={"help": "Mark as irrelevant."})
    direct_edit_loc: bool = field(
        default=False, metadata={"help": "Enable direct edit localization."}
    )
    num_threads: int = field(
        default=1, metadata={"help": "Number of threads to use for creating API requests."}
    )
    target_id: Optional[str] = field(
        default=None, metadata={"help": "Target ID."}
    )
    skip_existing: bool = field(
        default=False,
        metadata={
            "help": "Skip localization of instance id's which already contain a localization in the output file."
        },
    )
    mock: bool = field(
        default=False, metadata={"help": "Mock run to compute prompt tokens."}
    )
    model: str = field(
        default="gpt-4o-2024-05-13",
        metadata={
            "help": "Model to use.",
            "choices": [
                "gpt-4o-2024-05-13",
                "deepseek-coder",
                "gpt-4o-mini-2024-07-18",
                "claude-3-5-sonnet-20241022",
            ],
        },
    )
    backend: str = field(
        default="openai",
        metadata={
            "help": "Backend service.",
            "choices": ["openai", "deepseek", "anthropic"],
        },
    )
    dataset: str = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={
            "help": "Current supported dataset for evaluation.",
            "choices": ["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"],
        },
    )

    def __post_init__(self):
        # You can add validation for choices here if needed,
        # though it's often handled by argument parsing libraries directly.
        model_choices = [
            "gpt-4o-2024-05-13",
            "deepseek-coder",
            "gpt-4o-mini-2024-07-18",
            "claude-3-5-sonnet-20241022",
        ]
        if self.model not in model_choices:
            raise ValueError(
                f"Invalid model '{self.model}'. Choices are: {model_choices}"
            )

        backend_choices = ["openai", "deepseek", "anthropic"]
        if self.backend not in backend_choices:
            raise ValueError(
                f"Invalid backend '{self.backend}'. Choices are: {backend_choices}"
            )

        dataset_choices = ["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"]
        if self.dataset not in dataset_choices:
            raise ValueError(
                f"Invalid dataset '{self.dataset}'. Choices are: {dataset_choices}"
            )


@dataclass
class RetrievalArgs:
    """Arguments for the retrieval script."""

    # Required argument
    output_folder: str = field(
        metadata={"help": "The folder where output files will be stored."}
    )

    # Arguments with default values
    output_file: str = field(
        default="retrieve_locs.jsonl",
        metadata={"help": "The name of the output file."},
    )
    index_type: Literal["simple", "complex"] = field(
        default="simple",
        metadata={"help": "The type of index to use."},
    )
    filter_type: Literal["none", "given_files"] = field(
        default="none",
        metadata={"help": "The type of filtering to apply."},
    )
    filter_file: str = field(
        default="",
        metadata={"help": "File to use for filtering if filter_type is 'given_files'."},
    )
    chunk_size: int = field(
        default=512,
        metadata={"help": "The size of text chunks for indexing."},
    )
    chunk_overlap: int = field(
        default=0,
        metadata={"help": "The overlap between text chunks."},
    )
    num_threads: int = field(
        default=1,
        metadata={
            "help": "Number of threads for API requests (embedding token counts are only accurate when thread=1)."},
    )
    dataset: Literal["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"] = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={"help": "The dataset to use for retrieval."},
    )

    # Optional arguments that default to None
    filter_top_n: Optional[int] = field(
        default=None,
        metadata={"help": "Filter to the top N results."},
    )
    persist_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Directory to persist the index."},
    )
    target_id: Optional[str] = field(
        default=None,
        metadata={"help": "A specific instance ID to target."},
    )

    # Boolean flag
    mock: bool = field(
        default=False,
        metadata={"help": "Perform a mock run without executing main logic."},
    )


@dataclass
class CombineArgs:
    """Arguments for the combination script."""

    # Required arguments
    output_folder: str = field(
        metadata={"help": "The folder where the combined output file will be stored."}
    )
    retrieval_loc_file: str = field(
        metadata={"help": "Path to the localization file from the retrieval step."}
    )
    model_loc_file: str = field(
        metadata={"help": "Path to the localization file from the model step."}
    )
    top_n: int = field(
        metadata={"help": "The number of top results to combine for file-level combination."}
    )

    # Argument with a default value
    output_file: str = field(
        default="combined_locs.jsonl",
        metadata={"help": "The name of the final combined output file."}
    )


@dataclass
class RepairArgs:
    """Arguments for the code repair script."""

    # Required arguments
    loc_file: str = field(
        metadata={"help": "Path to the localization file."}
    )
    output_folder: str = field(
        metadata={"help": "Folder to store the output files."}
    )

    # Arguments with default values
    top_n: int = field(
        default=1,
        metadata={"help": "Top N locations to consider."}
    )
    context_window: int = field(
        default=10,
        metadata={"help": "Number of lines of context to include around a location."}
    )
    max_samples: int = field(
        default=20,
        metadata={"help": "Sampling budget for generation."}
    )
    select_id: int = field(
        default=-1,
        metadata={"help": "Index of the selected samples during post-processing."}
    )
    model: str = field(
        default="gpt-4o-2024-05-13",
        metadata={
            "help": "The model to use for generation.",
            "choices": [
                "gpt-4o-2024-05-13",
                "deepseek-coder",
                "gpt-4o-mini-2024-07-18",
                "claude-3-5-sonnet-20241022",
            ],
        },
    )
    backend: str = field(
        default="openai",
        metadata={
            "help": "The API backend to use.",
            "choices": ["openai", "deepseek", "anthropic"],
        },
    )
    num_threads: int = field(
        default=1,
        metadata={"help": "Number of threads for creating API requests."}
    )
    dataset: str = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={
            "help": "The dataset to use.",
            "choices": ["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"],
        },
    )

    # Optional string argument
    target_id: Optional[str] = field(
        default=None,
        metadata={"help": "A specific instance ID to target."}
    )

    # Boolean flags
    loc_interval: bool = field(
        default=False,
        metadata={"help": "Enable localization interval."}
    )
    gen_and_process: bool = field(
        default=False,
        metadata={"help": "Generate and process in a single run."}
    )
    post_process: bool = field(
        default=False,
        metadata={"help": "Run post-processing steps."}
    )
    add_space: bool = field(
        default=False,
        metadata={"help": "Add extra space in prompts."}
    )
    cot: bool = field(
        default=False,
        metadata={"help": "Use Chain-of-Thought prompting."}
    )
    fine_grain_loc_only: bool = field(
        default=False,
        metadata={"help": "Use only fine-grained locations."}
    )
    diff_format: bool = field(
        default=False,
        metadata={"help": "Use diff format for output."}
    )
    str_replace_format: bool = field(
        default=False,
        metadata={"help": "Use string replacement format."}
    )
    skip_greedy: bool = field(
        default=False,
        metadata={"help": "Skip the greedy decoding sample."}
    )
    sticky_scroll: bool = field(
        default=False,
        metadata={"help": "Enable sticky scroll context."}
    )
    mock: bool = field(
        default=False,
        metadata={"help": "Mock run to compute prompt tokens."}
    )

    def __post_init__(self):
        """Validate argument combinations after initialization."""
        if "deepseek" in self.model and self.backend != "deepseek":
            raise ValueError("Must specify `--backend deepseek` if using a DeepSeek model.")

        if self.diff_format and self.str_replace_format:
            raise ValueError("Cannot use both `diff_format` and `str_replace_format`.")

        if self.str_replace_format and self.backend != "anthropic":
            raise ValueError("`str_replace_format` is only supported with the 'anthropic' backend.")


@dataclass
class RegressionTestsArgs:
    # Required argument
    run_id: str = field(
        metadata={"help": "A unique identifier for the run."}
    )

    # Optional arguments
    predictions_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the patch file with normalized patches."}
    )
    output_file: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the output file."}
    )
    regression_tests: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the regression tests file."}
    )
    instance_ids: Optional[List[str]] = field(
        default=None,
        metadata={"help": "Instance IDs to run (space separated). If not provided, all instances will be run."}
    )

    # Arguments with default values
    num_workers: int = field(
        default=12,
        metadata={"help": "Number of worker processes to use."}
    )
    timeout: int = field(
        default=1200,
        metadata={"help": "Timeout for running tests in seconds."}
    )
    dataset: Literal["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"] = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={"help": "The dataset to use."}
    )

    # Boolean flags
    filter: bool = field(
        default=False,
        metadata={"help": "Filter instances based on some criteria."}
    )
    load: bool = field(
        default=False,
        metadata={"help": "Load existing results."}
    )


@dataclass
class SelectRegressionTestsArgs:
    """Arguments for a model run."""

    # Required arguments
    output_folder: str = field(
        metadata={"help": "The folder where output files will be stored."}
    )
    passing_tests: str = field(
        metadata={"help": "Path to the file containing passing test information."}
    )

    # Arguments with default values
    model: Literal[
        "gpt-4o-2024-05-13",
        "deepseek-coder",
        "gpt-4o-mini-2024-07-18",
        "claude-3-5-sonnet-20241022",
    ] = field(
        default="gpt-4o-2024-05-13",
        metadata={"help": "The model to use for the run."}
    )
    backend: Literal["openai", "deepseek", "anthropic"] = field(
        default="openai",
        metadata={"help": "The backend service to use."}
    )
    dataset: Literal["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"] = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={"help": "The dataset to use."}
    )

    # Optional arguments that default to None
    target_id: Optional[str] = field(
        default=None,
        metadata={"help": "A specific instance ID to target."}
    )
    instance_ids: Optional[List[str]] = field(
        default=None,
        metadata={"help": "Specific instance IDs to run (space separated)."}
    )

    # Boolean flag
    mock: bool = field(
        default=False,
        metadata={"help": "Perform a mock run to compute prompt tokens."}
    )

    def __post_init__(self):
        """Post-initialization validation for argument consistency."""
        if "deepseek" in self.model and self.backend != "deepseek":
            raise ValueError("Must specify `--backend deepseek` if using a DeepSeek model.")


@dataclass
class GenerateTestArgs:
    """Arguments for the test generation script."""

    # Required argument
    output_folder: str = field(
        metadata={"help": "The folder where output files will be stored."}
    )

    # Arguments with default values
    max_samples: int = field(
        default=20,
        metadata={"help": "Sampling budget for generation."}
    )
    select_id: int = field(
        default=-1,
        metadata={"help": "Index of the selected samples during post-processing."}
    )
    model: Literal[
        "gpt-4o-2024-05-13",
        "deepseek-coder",
        "gpt-4o-mini-2024-07-18",
        "claude-3-5-sonnet-20241022",
    ] = field(
        default="gpt-4o-2024-05-13",
        metadata={"help": "The model to use for generation."}
    )
    backend: Literal["openai", "deepseek", "anthropic"] = field(
        default="openai",
        metadata={"help": "The backend service to use."}
    )
    num_threads: int = field(
        default=1,
        metadata={"help": "Number of threads for creating API requests."}
    )
    dataset: Literal["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"] = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={"help": "The dataset to use."}
    )

    # Optional arguments that default to None
    output_file: Optional[str] = field(
        default=None,
        metadata={"help": "The name of the output file."}
    )
    target_id: Optional[str] = field(
        default=None,
        metadata={"help": "A specific instance ID to target."}
    )

    # Boolean flags
    skip_greedy: bool = field(
        default=False,
        metadata={"help": "Skip the greedy decoding sample."}
    )
    mock: bool = field(
        default=False,
        metadata={"help": "Perform a mock run to compute prompt tokens."}
    )
    select: bool = field(
        default=False,
        metadata={"help": "Enable selection of samples."}
    )


@dataclass
class RunReproductionTestsArgs:
    """Arguments for running reproduction tests."""
    run_id: str = field(
        metadata={"help": "A unique identifier for the run."}
    )
    # Arguments with default values
    num_workers: int = field(
        default=12,
        metadata={"help": "Number of worker processes to use."}
    )
    timeout: int = field(
        default=600,
        metadata={"help": "Timeout for running tests in seconds."}
    )
    dataset: Literal["princeton-nlp/SWE-bench_Lite", "princeton-nlp/SWE-bench_Verified"] = field(
        default="princeton-nlp/SWE-bench_Lite",
        metadata={"help": "The dataset to use for the tests."}
    )

    # Optional arguments that default to None
    predictions_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the patch file."}
    )
    instance_ids: Optional[List[str]] = field(
        default=None,
        metadata={"help": "Specific instance IDs to run (space separated)."}
    )
    test_jsonl: Optional[str] = field(
        default=None,
        metadata={"help": "Path to a JSONL file with test definitions."}
    )

    # Boolean flags
    testing: bool = field(
        default=False,
        metadata={"help": "If true, do not apply the model patch."}
    )
    load: bool = field(
        default=False,
        metadata={"help": "Load existing results instead of running new tests."}
    )


@dataclass
class RerankArgs:
    """Arguments for the reranking script."""

    # Optional arguments that default to None
    patch_folder: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the folder containing patch files."}
    )
    target: Optional[str] = field(
        default=None,
        metadata={"help": "The target for reranking."}
    )

    # Arguments with default values
    num_samples: int = field(
        default=11,
        metadata={"help": "The number of samples to consider."}
    )
    output_file: str = field(
        default="all_preds.jsonl",
        metadata={"help": "The name of the output file for all predictions."}
    )

    # Boolean flags
    deduplicate: bool = field(
        default=False,
        metadata={"help": "If true, deduplicate samples."}
    )
    regression: bool = field(
        default=False,
        metadata={"help": "If true, run regression reranking."}
    )
    reproduction: bool = field(
        default=False,
        metadata={"help": "If true, run reproduction reranking."}
    )
