using System;
using UnityEngine;

namespace CortexAI
{
    public static class StorageService
    {
        private const string UserProfileKey = "cortexai.user_profile";

        public static void SaveUserProfile(UserProfile profile)
        {
            if (profile == null) return;
            try
            {
                var json = JsonUtility.ToJson(profile);
                PlayerPrefs.SetString(UserProfileKey, json);
                PlayerPrefs.Save();
            }
            catch (Exception)
            {
            }
        }

        public static UserProfile LoadUserProfile()
        {
            try
            {
                if (!PlayerPrefs.HasKey(UserProfileKey)) return null;
                var json = PlayerPrefs.GetString(UserProfileKey, string.Empty);
                if (string.IsNullOrEmpty(json)) return null;
                return JsonUtility.FromJson<UserProfile>(json);
            }
            catch (Exception)
            {
                return null;
            }
        }

        public static void ClearUserProfile()
        {
            PlayerPrefs.DeleteKey(UserProfileKey);
            PlayerPrefs.Save();
        }
    }
}

