import * as admin from 'firebase-admin';
import * as functions from 'firebase-functions';

admin.initializeApp();

export const helloWorld = functions.https.onRequest(async (req, res) => {
  res.json({ message: 'Hello from Firebase Functions!' });
});

export const onUserCreate = functions.auth.user().onCreate(async (user) => {
  const userDoc = {
    uid: user.uid,
    email: user.email ?? null,
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  };
  await admin.firestore().doc(`users/${user.uid}`).set(userDoc, { merge: true });
});

export const sanitizeUserData = functions.firestore
  .document('users/{userId}')
  .onWrite(async (change, context) => {
    const userId = context.params.userId as string;
    const afterData = change.after.exists ? change.after.data() : null;
    if (!afterData) return;

    const sanitized = { ...afterData } as Record<string, unknown>;
    delete sanitized['isAdmin'];

    await admin.firestore().doc(`users/${userId}`).set(sanitized, { merge: true });
  });
