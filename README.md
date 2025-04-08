# Comments_Beliefs
Stances extraction from comments data



####

### **1. README: How to Access My MongoDB Database**
## **🚀 Step 1: Start MongoDB**
Before accessing your database, you must start MongoDB.

If using **Homebrew**:
```bash
brew services start mongodb-community
```
If running manually with your **external SSD storage**:
```bash
mongod --dbpath "/Volumes/Untitled/mongo_data"
```
OR
```bash
mongod --dbpath "/Volumes/T7 Shield/mongo_data"
```
Check that MongoDB is running:
```bash
brew services list
```

---

## **🔑 Step 2: Open a Connection to MongoDB**
Once MongoDB is running, open the MongoDB shell:

```bash
mongosh
```
If connecting to a **specific database**:
```bash
mongosh "mongodb://127.0.0.1:27017"
```

---

## **📂 Step 3: List Databases & Collections**
Show available **databases**:
```javascript
show dbs
```
Switch to the **database**:
```javascript
use Comments
```
Show **collections** inside the database:
```javascript
show collections
```

---

## **🔎 Step 4: Basic Queries**
### ✅ **Check the number of documents in a collection**
```javascript
db.Breitbart.countDocuments()
```

### ✅ **View a sample document**
```javascript
db.Breitbart.findOne()
```

### ✅ **Retrieve multiple documents**
```javascript
db.Breitbart.find().limit(5).pretty()
```

---

## **📊 Step 5: Run Aggregation Queries**
For example, **group by user_id and count their comments**:
```javascript
db.Breitbart.aggregate([
    { "$group": { "_id": "$user_id", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } },
    { "$limit": 10 }
])
```

---

## **🚦 Step 6: Monitor Running Queries**
If a query is **taking too long**, check its status:
```javascript
db.currentOp({ "active": true })
```
To **stop a running query**, first find its **opid** (from `currentOp`), then:
```javascript
db.killOp(opid)
```

---

## **💾 Step 7: Export & Save Query Results**
If running queries in **Python**, save results as JSON or CSV:
```python
import pandas as pd

df = pd.DataFrame(results_list)  # Convert results to DataFrame
df.to_csv("breitbart_commenters.csv", index=False)  # Save to CSV
df.to_json("breitbart_commenters.json", orient="records")  # Save to JSON
```

---

## **🛑 Step 8: Stop MongoDB (If Needed)**
To **stop the MongoDB service**:
```bash
brew services stop mongodb-community
```
Or manually:
```bash
mongod --shutdown
```

---

## **💡 Additional Notes**
- Queries on large datasets **may take time**, so **use indexes** for better performance.
- Always **backup important data** before making bulk modifications.
- If a query takes **too long**, optimize with `.explain("executionStats")`.




----------------------------------------------------------------------------

### **User Aggregation for Breitbart Comments** (March 5, 2025)  

The script (users_database.py) extracts and aggregates user-level data from the **Breitbart comments** collection in the `Comments` database. The results are stored in a new `Users` database, maintaining the same collection structure.  

- **Optimized MongoDB aggregation** to compute user stats (comment count, likes, article interactions, etc.).  
- **Indexes added** to Comments / Breitbart for efficient querying (`user_id`, `comment_id`, `createdAt`).  
- **Data stored efficiently**, keeping only essential fields + all infos concerning the user.
- **Uses `$merge` with `whenMatched: "merge"`** to update users without overwriting existing data.  

{
    "_id": "65893635",  // user_id
    "user_names": ["LeonTrotsky1"],  // List of all usernames used by this user
    "user_about": "",
    "user_avatar": "https://c.disquscdn.com/uploads/users/6589/3635/avatar92.jpg?1377116939",
    "user_disable3rdPartyTrackers": false,
    "user_isAnonymous": false,
    "user_isPowerContributor": false,
    "user_isPrimary": true,
    "user_isPrivate": false,
    "user_joinedAt": "2013-08-05T14:28:26Z",
    "user_location": "",
    "user_profileURL": "https://disqus.com/by/LeonTrotsky1/",
    
    // Aggregated user stats
    "comments_count": 1234,  // Total comments made by this user
    "likes_count": 2567,  // Total likes received on all comments
    "first_comment": "2013-08-14T01:24:32Z",  // Timestamp of first comment
    "last_comment": "2025-03-04T12:30:45Z"  // Timestamp of latest comment
}
