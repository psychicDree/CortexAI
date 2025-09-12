using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace CortexAI
{
    public static class BackendClient
    {
        private const string ApiBaseKey = "cortexai.api_base";

        public static string GetApiBase()
        {
            var overrideBase = PlayerPrefs.GetString(ApiBaseKey, string.Empty);
            if (!string.IsNullOrWhiteSpace(overrideBase)) return overrideBase;
            return "http://localhost:8000";
        }

        public static IEnumerator PostOnboarding(UserProfile profile)
        {
            if (profile == null) yield break;

            var url = GetApiBase().TrimEnd('/') + "/onboarding/";
            var payload = new OnboardingPayload
            {
                client_user_id = profile.UserId,
                display_name = profile.DisplayName,
                age = profile.Age
            };
            var json = JsonUtility.ToJson(payload);
            var bodyRaw = Encoding.UTF8.GetBytes(json);

            using (var req = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
            {
                req.uploadHandler = new UploadHandlerRaw(bodyRaw);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");

                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogWarning($"Onboarding POST failed: {req.responseCode} {req.error}");
                }
                else
                {
                    Debug.Log($"Onboarding POST success: {req.responseCode}");
                }
            }
        }

        [System.Serializable]
        private class OnboardingPayload
        {
            public string client_user_id;
            public string display_name;
            public int age;
        }
    }
}

