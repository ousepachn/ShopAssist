import ray
from pathlib import Path
from pandas.io.formats import format

EFS_DIR = "/Users/gallopade/Documents/hackathon/"
DOCS_DIR = Path(EFS_DIR, "docs.ray.io/en/master")


def extract_sections(path):
    return [
        {
            "source": "https://docs.ray.io/en/master/rllib/rllib-env.html#environments",
            "text": "\nEnvironments#\nRLlib works with several different types of environments, including Farama-Foundation Gymnasium, user-defined, multi-agent, and also batched environments.\nTip\nNot all environments work with all algorithms. Check out the algorithm overview for more information.\n",
        }
    ]


print(DOCS_DIR)
ds = ray.data.from_items(
    [{"path": path} for path in DOCS_DIR.rglob("*.html") if not path.is_dir()]
)
print(f"{ds.count()} documents")

extract_sections(DOCS_DIR)
