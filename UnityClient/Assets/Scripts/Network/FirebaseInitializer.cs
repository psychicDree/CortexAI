using System.Threading.Tasks;
using Firebase;
using UnityEngine;

namespace Client.Network
{
    public class FirebaseInitializer : MonoBehaviour
    {
        private static bool _initialized;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void EnsureInitialized()
        {
            if (_initialized) return;
            _initialized = true;
            _ = InitializeAsync();
        }

        private static async Task InitializeAsync()
        {
            var status = await FirebaseApp.CheckAndFixDependenciesAsync();
            if (status != DependencyStatus.Available)
            {
                Debug.LogError($"Firebase dependencies not available: {status}");
                return;
            }
            _ = FirebaseApp.DefaultInstance; // force init
            Debug.Log("Firebase initialized");
        }
    }
}

