"""
Seed script for the "Two Sum" problem.

Run from backend/:
    source venv/bin/activate
    python scripts/seed_problem_two_sum.py
"""

from pathlib import Path
import sys

# Ensure "app" package is importable when running as a script path.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.database import Base, SessionLocal, engine
from app.db.models import Problem, ProblemList, ProblemListProblem
import app.db.models  # noqa: F401  # ensure all models are registered before create_all


TWO_SUM = {
    "title": "Two Sum",
    "category": "Arrays, Strings and Hashing",
    "difficulty": "Easy",
    "description": """Given an array of integers nums and an integer target, return the indices i and j such that nums[i] + nums[j] == target and i != j.
You may assume that every input has exactly one pair of indices i and j that satisfy the condition.
Return the answer with the smaller index first.

Example 1:
Input: nums = [1, 2, 3, 6], target = 7
Output: [0,3]
Explanation: nums[0] + nums[3] == 7, so we return [0, 3].

Example 2:
Input: nums = [7, 3, 8, 2], target = 11
Output: [1,2]

Example 3:
Input: nums = [2,2], target = 4
Output: [0,1]

Constraints:
- 2 <= nums.length <= 1000
- -10,000,000 <= nums[i] <= 10,000,000
- -10,000,000 <= target <= 10,000,000
""",
    "starter_code": {
        "python": """class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        
""",
        "javascript": """class Solution {
  /**
   * @param {number[]} nums
   * @param {number} target
   * @return {number[]}
   */
  twoSum = function(nums, target) {
      
  };
}

// Please don’t remove below line of code
module.exports = { Solution };
""",
        "java": """class Solution {
    public int[] twoSum(int[] nums, int target) {
        
    }
}
""",
        "cpp": """class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        
    }
};
""",
    },
}

# Add this problem to these existing seeded lists when they exist.
TARGET_LIST_IDS = ("blind_75", "taro_75", "neetcode_150", "google_50", "meta_50", "amazon_50", "apple_30", "microsoft_30")


def seed_two_sum() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        problem = db.query(Problem).filter(Problem.title == TWO_SUM["title"]).first()

        if problem is None:
            problem = Problem(
                title=TWO_SUM["title"],
                description=TWO_SUM["description"],
                difficulty=TWO_SUM["difficulty"],
                category=TWO_SUM["category"],
                starter_code=TWO_SUM["starter_code"],
            )
            db.add(problem)
            db.flush()
            print("Inserted problem: Two Sum")
        else:
            problem.description = TWO_SUM["description"]
            problem.difficulty = TWO_SUM["difficulty"]
            problem.category = TWO_SUM["category"]
            problem.starter_code = TWO_SUM["starter_code"]
            db.flush()
            print("Updated problem: Two Sum")

        linked = 0
        skipped = 0
        for list_id in TARGET_LIST_IDS:
            problem_list = db.query(ProblemList).filter(ProblemList.id == list_id).first()
            if problem_list is None:
                continue

            existing_link = (
                db.query(ProblemListProblem)
                .filter(
                    ProblemListProblem.problem_list_id == list_id,
                    ProblemListProblem.problem_id == problem.id,
                )
                .first()
            )

            if existing_link:
                skipped += 1
                continue

            db.add(ProblemListProblem(problem_list_id=list_id, problem_id=problem.id))
            linked += 1

        db.commit()
        print(f"Done. Linked to lists: {linked}, Existing links skipped: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_two_sum()
