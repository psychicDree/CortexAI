using UnityEngine;

namespace CortexAI
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [SerializeField]
        private SessionManager sessionManager;

        [SerializeField]
        private UIManager uiManager;

        [SerializeField]
        private OnboardingManager onboardingManager;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);

            if (sessionManager == null)
            {
                sessionManager = FindObjectOfType<SessionManager>();
            }

            if (uiManager == null)
            {
                uiManager = FindObjectOfType<UIManager>();
            }

            if (onboardingManager == null)
            {
                onboardingManager = FindObjectOfType<OnboardingManager>();
            }

            if (onboardingManager != null)
            {
                onboardingManager.StartOnboardingFlow();
            }
        }

        public void StartNewSession()
        {
            if (sessionManager == null) return;
            sessionManager.StartSession();
            if (uiManager != null)
            {
                uiManager.ShowSessionUI();
            }
        }

        public void EndCurrentSession()
        {
            if (sessionManager == null) return;
            sessionManager.EndSession();
            if (uiManager != null)
            {
                uiManager.ShowHomeUI();
            }
        }
    }
}

