using UnityEngine;

namespace CortexAI
{
    public class UIManager : MonoBehaviour
    {
        [SerializeField]
        private GameObject homePanel;

        [SerializeField]
        private GameObject sessionPanel;

        public void ShowHomeUI()
        {
            if (homePanel != null) homePanel.SetActive(true);
            if (sessionPanel != null) sessionPanel.SetActive(false);
        }

        public void ShowSessionUI()
        {
            if (homePanel != null) homePanel.SetActive(false);
            if (sessionPanel != null) sessionPanel.SetActive(true);
        }
    }
}

