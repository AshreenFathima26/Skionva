from datetime import datetime
from database.mongo import progress_collection


def save_progress(uid, analysis_data):

    today = datetime.now().strftime("%Y-%m-%d")

    document = {
        "uid": uid,
        "date": today,
        "overall_score": analysis_data["overall_score"],
        "conditions": analysis_data["conditions"],
        "final_suggestion": analysis_data["final_suggestion"],
        "image": analysis_data["image"],
        "saved_at": datetime.now()
    }

    progress_collection.update_one(
        {
            "uid": uid,
            "date": today
        },
        {
            "$set": document
        },
        upsert=True
    )

    return True


def get_progress(uid):

    progress = list(
        progress_collection.find(
            {
                "uid": uid
            },
            {
                "_id": 0
            }
        ).sort("date", 1)
    )

    return progress
