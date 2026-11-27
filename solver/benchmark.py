import signal
import time
from pathlib import Path

from solver.connect4 import Position
from solver.negamax import negamax

HERE = Path(__file__).parent
DATASET = HERE / "dataset"
RESULTS = HERE / "results"

# Pons test, L = moves played: 3 end, 2 middle, 1 beginning; R = difficulty
Test_L3_R1 = DATASET / "Test_L3_R1"  # end-easy
Test_L2_R1 = DATASET / "Test_L2_R1"  # middle-easy
Test_L2_R2 = DATASET / "Test_L2_R2"  # middle-medium
Test_L1_R1 = DATASET / "Test_L1_R1"  # begin-easy
Test_L1_R2 = DATASET / "Test_L1_R2"  # begin-medium
Test_L1_R3 = DATASET / "Test_L1_R3"  # begin-hard
Test_All = [Test_L3_R1, Test_L2_R1, Test_L2_R2, Test_L1_R1, Test_L1_R2, Test_L1_R3]

Benchmark_Files = [Test_L3_R1, Test_L2_R1]
Benchmark_Methods = [negamax]
Max_Positions = None  # None for all
Timeout = 10  # seconds per position, None for no limit


def _on_timeout(signum, frame):
    raise TimeoutError


signal.signal(signal.SIGALRM, _on_timeout)


def solve(method, pos: Position, timeout: int | None) -> int | None:
    signal.alarm(timeout or 0)  # 0 = no alarm
    try:
        return method(pos)
    except TimeoutError:
        return None
    finally:
        signal.alarm(0)


def load(file: Path, limit: int | None = None) -> list[tuple[str, int]]:
    file_lines = file.read_text().splitlines()
    if limit is None:
        limit = len(file_lines)

    positions = []
    for line in file_lines[:limit]:
        seq, score = line.split()
        positions.append((seq, int(score)))
    return positions


# one csv and a summary file for each method
def main(timeout: int | None = Timeout) -> None:
    RESULTS.mkdir(exist_ok=True)
    for method in Benchmark_Methods:
        log_time = time.strftime('%Y%m%d_%H%M%S')
        result_out_path = RESULTS / f"benchmark_{method.__name__}_{log_time}.csv"
        summary_out_path = RESULTS / f"benchmark_summary_{method.__name__}_{log_time}.txt"

        with open(result_out_path, "w") as result_out, open(summary_out_path, "w") as summary_out:
            result_out.write("method,file,position,expected,score,correct,time_s\n")

            for file in Benchmark_Files:
                positions = load(file, Max_Positions)
                n_correct, n_timeout, total_time = 0, 0, 0.0
                for seq, expected in positions:
                    pos = Position()
                    pos.sequence_encode(seq)

                    start = time.perf_counter()
                    score = solve(method, pos, timeout)
                    elapsed = time.perf_counter() - start

                    if score is None:
                        n_timeout += 1
                        result_out.write(
                            f"{method.__name__},{file.name},{seq},{expected},timeout,False,{elapsed:.9f}\n")
                        continue

                    correct = (score == expected)
                    n_correct += correct
                    total_time += elapsed
                    result_out.write(
                        f"{method.__name__},{file.name},{seq},{expected},{score},{correct},{elapsed:.9f}\n")

                n = len(positions)
                n_solved = n - n_timeout
                mean_time = total_time / n_solved if n_solved else float("nan")
                summary = (f"{method.__name__:10} {file.name}: {n_correct}/{n} correct, "
                           f"{n_timeout} timeout (>{timeout}s), mean time {mean_time:.9f} (solved only)")
                print(summary)
                summary_out.write(f"# {summary}\n")

        print(f"results written to {result_out_path}, and summary to {summary_out_path}")


if __name__ == "__main__":
    main()
