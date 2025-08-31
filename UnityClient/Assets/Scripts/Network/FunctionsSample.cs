using System.Threading.Tasks;
using Firebase;
using Firebase.Functions;

namespace Client.Network
{
    public class FunctionsSample
    {
        private readonly FirebaseFunctions _functions;

        public FunctionsSample()
        {
            _functions = FirebaseFunctions.DefaultInstance;
        }

        public async Task<string> HelloAsync()
        {
            var result = await _functions.GetHttpsCallable("helloWorld").CallAsync(null);
            return result?.Data?.ToString() ?? string.Empty;
        }
    }
}

