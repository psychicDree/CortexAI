using UnityEngine;

namespace CortexAI
{
    public class AuthManager : MonoBehaviour
    {
        public UserProfile CurrentUser { get; private set; }

        public bool HasExistingUser()
        {
            CurrentUser = StorageService.LoadUserProfile();
            return CurrentUser != null;
        }

        public bool TrySignInExisting()
        {
            CurrentUser = StorageService.LoadUserProfile();
            return CurrentUser != null;
        }

        public bool CreateAndSignIn(string displayName, int age)
        {
            if (string.IsNullOrWhiteSpace(displayName) || age < 0)
            {
                return false;
            }

            var profile = UserProfile.CreateNew(displayName.Trim(), age);
            StorageService.SaveUserProfile(profile);
            CurrentUser = profile;

            // Fire-and-forget onboarding POST to backend
            var mb = GetComponent<MonoBehaviour>();
            if (mb != null)
            {
                mb.StartCoroutine(BackendClient.PostOnboarding(profile));
            }
            return true;
        }

        public void SignOut()
        {
            CurrentUser = null;
        }
    }
}

