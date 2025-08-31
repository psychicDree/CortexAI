using System;
using UnityEngine;

namespace CortexAI
{
    public class SessionManager : MonoBehaviour
    {
        private DateTime? sessionStartUtc;
        private TimeSpan lastSessionDuration;

        public bool IsSessionActive => sessionStartUtc.HasValue;
        public TimeSpan LastSessionDuration => lastSessionDuration;

        public void StartSession()
        {
            if (IsSessionActive) return;
            sessionStartUtc = DateTime.UtcNow;
        }

        public void EndSession()
        {
            if (!IsSessionActive) return;
            lastSessionDuration = DateTime.UtcNow - sessionStartUtc.Value;
            sessionStartUtc = null;
        }
    }
}

