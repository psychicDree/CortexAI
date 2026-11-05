using System;
using System.Security.Cryptography;
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

        // Proves ownership of the backend onboarding profile. Never shown to the user.
        public string DeviceSecret;

        public static UserProfile CreateNew(string displayName, int age)
        {
            return new UserProfile
            {
                UserId = Guid.NewGuid().ToString("N"),
                DisplayName = displayName,
                Age = Mathf.Max(0, age),
                CreatedAtUtc = DateTime.UtcNow,
                DeviceSecret = NewDeviceSecret()
            };
        }

        public static string NewDeviceSecret()
        {
            var bytes = new byte[32];
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(bytes);
            }
            return BitConverter.ToString(bytes).Replace("-", string.Empty).ToLowerInvariant();
        }
    }
}

