import * as admin from 'firebase-admin';
import * as functions from 'firebase-functions';
import { FieldValue } from 'firebase-admin/firestore';

admin.initializeApp();

export const helloWorld = functions.https.onRequest(async (req, res) => {
  res.json({ message: 'Hello from Firebase Functions!' });
});

export const onUserCreate = functions.auth.user().onCreate(async (user) => {
  const userDoc = {
    uid: user.uid,
    email: user.email ?? null,
    createdAt: FieldValue.serverTimestamp()
  };
  await admin.firestore().doc(`users/${user.uid}`).set(userDoc, { merge: true });
});

// Clients must not set isAdmin on their own user document. Only acts when the
// field is present, so its own update does not trigger another write.
export const sanitizeUserData = functions.firestore
  .document('users/{userId}')
  .onWrite(async (change) => {
    if (!change.after.exists) return;
    if (change.after.get('isAdmin') === undefined) return;

    await change.after.ref.update({ isAdmin: FieldValue.delete() });
  });
