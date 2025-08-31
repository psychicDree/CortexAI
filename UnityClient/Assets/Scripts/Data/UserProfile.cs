using System;
using UnityEngine;

namespace CortexAI
{
    [Serializable]
    public class UserProfile
    {
        public string UserId;
        public string DisplayName;
        public int Age;
        public DateTime CreatedAtUtc;

        public static UserProfile CreateNew(string displayName, int age)
        {
            return new UserProfile
            {
                UserId = Guid.NewGuid().ToString("N"),
                DisplayName = displayName,
                Age = Mathf.Max(0, age),
                CreatedAtUtc = DateTime.UtcNow
            };
        }
    }
}

