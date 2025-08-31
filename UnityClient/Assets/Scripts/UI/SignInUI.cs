using System;
using UnityEngine;
using UnityEngine.UI;

namespace CortexAI
{
    public class SignInUI : MonoBehaviour
    {
        [SerializeField]
        private Button signInButton;

        [SerializeField]
        private Button backButton;

        [SerializeField]
        private Text errorText;

        private Action onSignIn;
        private Action onBack;

        public void Initialize(Action onSignIn, Action onBack)
        {
            this.onSignIn = onSignIn;
            this.onBack = onBack;

            if (errorText != null) errorText.text = string.Empty;

            if (signInButton != null)
            {
                signInButton.onClick.RemoveAllListeners();
                signInButton.onClick.AddListener(() => this.onSignIn?.Invoke());
            }

            if (backButton != null)
            {
                backButton.onClick.RemoveAllListeners();
                backButton.onClick.AddListener(() => this.onBack?.Invoke());
            }
        }

        public void ShowError(string message)
        {
            if (errorText != null)
            {
                errorText.text = message ?? string.Empty;
            }
        }
    }
}

