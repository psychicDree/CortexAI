using UnityEngine;

namespace CortexAI
{
    public class OnboardingManager : MonoBehaviour
    {
        [SerializeField]
        private AuthManager authManager;

        [SerializeField]
        private UIManager uiManager;

        [SerializeField]
        private OnboardingUI onboardingUI;

        [SerializeField]
        private SignInUI signInUI;

        private void Awake()
        {
            if (authManager == null) authManager = FindObjectOfType<AuthManager>();
            if (uiManager == null) uiManager = FindObjectOfType<UIManager>();
            if (onboardingUI == null) onboardingUI = FindObjectOfType<OnboardingUI>(true);
            if (signInUI == null) signInUI = FindObjectOfType<SignInUI>(true);
        }

        public void StartOnboardingFlow()
        {
            if (authManager == null) return;

            if (authManager.HasExistingUser())
            {
                // Analytics: existing user resumed
                Debug.Log("Onboarding: Existing user detected");
                if (uiManager != null) uiManager.ShowHomeUI();
                return;
            }

            ShowOnboardingSurvey();
        }

        private void ShowOnboardingSurvey()
        {
            if (onboardingUI != null)
            {
                onboardingUI.gameObject.SetActive(true);
                onboardingUI.Initialize(
                    onCreate: (name, age) =>
                    {
                        if (authManager.CreateAndSignIn(name, age))
                        {
                            Debug.Log("Onboarding: Created profile and posted to backend");
                            onboardingUI.gameObject.SetActive(false);
                            if (uiManager != null) uiManager.ShowHomeUI();
                        }
                        else
                        {
                            onboardingUI.ShowValidationError("Please enter a valid name and age.");
                        }
                    },
                    onExistingUser: () =>
                    {
                        onboardingUI.gameObject.SetActive(false);
                        Debug.Log("Onboarding: Existing user button clicked");
                        ShowSignIn();
                    }
                );
            }
        }

        private void ShowSignIn()
        {
            if (signInUI != null)
            {
                signInUI.gameObject.SetActive(true);
                signInUI.Initialize(
                    onSignIn: () =>
                    {
                        if (authManager.TrySignInExisting())
                        {
                            signInUI.gameObject.SetActive(false);
                            if (uiManager != null) uiManager.ShowHomeUI();
                        }
                        else
                        {
                            signInUI.ShowError("No existing user found on this device.");
                        }
                    },
                    onBack: () =>
                    {
                        signInUI.gameObject.SetActive(false);
                        ShowOnboardingSurvey();
                    }
                );
            }
        }
    }
}

