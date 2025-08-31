using System.Collections.Generic;
using System.Threading.Tasks;
using Firebase;
using Firebase.Firestore;
using UnityEngine;

namespace Client.Network
{
    public class FirestoreSample
    {
        private readonly FirebaseFirestore _db;

        public FirestoreSample()
        {
            _db = FirebaseFirestore.DefaultInstance;
        }

        public async Task WriteUserAsync(string userId)
        {
            var dict = new Dictionary<string, object>
            {
                { "hello", "world" },
                { "updatedAt", FieldValue.ServerTimestamp }
            };
            await _db.Document($"users/{userId}").SetAsync(dict, SetOptions.MergeAll);
        }

        public async Task<DocumentSnapshot> ReadUserAsync(string userId)
        {
            return await _db.Document($"users/{userId}").GetSnapshotAsync();
        }
    }
}

