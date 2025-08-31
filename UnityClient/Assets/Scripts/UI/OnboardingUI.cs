using System;
using UnityEngine;
using UnityEngine.UI;

namespace CortexAI
{
    public class OnboardingUI : MonoBehaviour
    {
        [SerializeField]
        private InputField nameInput;

        [SerializeField]
        private InputField ageInput;

        [SerializeField]
        private Button createButton;

        [SerializeField]
        private Button existingUserButton;

        [SerializeField]
        private Text errorText;

        private Action<string, int> onCreate;
        private Action onExistingUser;

        private void Reset()
        {
            errorText.text = string.Empty;
        }

        public void Initialize(Action<string, int> onCreate, Action onExistingUser)
        {
            this.onCreate = onCreate;
            this.onExistingUser = onExistingUser;

            if (errorText != null) errorText.text = string.Empty;

            if (createButton != null)
            {
                createButton.onClick.RemoveAllListeners();
                createButton.onClick.AddListener(() =>
                {
                    var name = nameInput != null ? nameInput.text : string.Empty;
                    var ageStr = ageInput != null ? ageInput.text : string.Empty;
                    int age = 0;
                    int.TryParse(ageStr, out age);
                    onCreate?.Invoke(name, age);
                });
            }

            if (existingUserButton != null)
            {
                existingUserButton.onClick.RemoveAllListeners();
                existingUserButton.onClick.AddListener(() => onExistingUser?.Invoke());
            }
        }

        public void ShowValidationError(string message)
        {
            if (errorText != null)
            {
                errorText.text = message ?? string.Empty;
            }
        }
    }
}

