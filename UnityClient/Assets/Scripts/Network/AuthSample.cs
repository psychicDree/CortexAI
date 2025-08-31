using System.Threading.Tasks;
using Firebase;
using Firebase.Auth;
using UnityEngine;

namespace Client.Network
{
    public class AuthSample : MonoBehaviour
    {
        private FirebaseAuth _auth;

        private async void Awake()
        {
            await EnsureFirebaseAsync();
            _auth = FirebaseAuth.DefaultInstance;
        }

        private static async Task EnsureFirebaseAsync()
        {
            var status = await FirebaseApp.CheckAndFixDependenciesAsync();
            if (status != DependencyStatus.Available)
            {
                Debug.LogError($"Firebase dependencies not available: {status}");
            }
        }

        public async Task SignInAnonymousAsync()
        {
            var result = await _auth.SignInAnonymouslyAsync();
            Debug.Log($"Signed in uid={result.User.UserId}");
        }

        public async Task SignOutAsync()
        {
            await Task.Yield();
            _auth.SignOut();
        }
    }
}

