using System.Threading.Tasks;
using Firebase;
using Firebase.Storage;

namespace Client.Network
{
    public class StorageSample
    {
        private readonly FirebaseStorage _storage;

        public StorageSample()
        {
            _storage = FirebaseStorage.DefaultInstance;
        }

        public async Task UploadPngAsync(string userId, byte[] bytes)
        {
            var path = $"userContent/{userId}/image.png";
            var task = _storage.GetReference(path).PutBytesAsync(bytes);
            await task;
        }
    }
}

