// NanoPro Email Relay — Google Apps Script (v3: attachments + colored HTML)
// Update: script.google.com → your relay project → replace code → Save
//         → Deploy → Manage deployments → edit (pencil) → Version: New version → Deploy

var RELAY_SECRET = "49c62e3dcd3fe486d5de96f1123df5ad";
var TO_DEFAULT = "nanoproaistudio@gmail.com";
var MAX_ATTACH_BYTES = 5 * 1024 * 1024; // 5 MB

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    if (body.secret !== RELAY_SECRET) {
      return ContentService.createTextOutput(JSON.stringify({ ok: false, error: "unauthorized" }));
    }
    var to = body.to || TO_DEFAULT;
    var opts = {};
    // v3: colored HTML body support (plain text stays as fallback)
    if (body.htmlBody) { opts.htmlBody = body.htmlBody; }
    // Attach only if attachment content is present and under 5 MB; otherwise body-only
    if (body.attachmentName && body.attachmentText) {
      var approxBytes = Math.ceil(body.attachmentText.length * 0.75 * 1.37);
      if (approxBytes < MAX_ATTACH_BYTES) {
        opts.attachments = [Utilities.newBlob(body.attachmentText, "text/plain", body.attachmentName)];
      }
    }
    GmailApp.sendEmail(to, body.subject, body.text, opts);
    return ContentService.createTextOutput(JSON.stringify({ ok: true, to: to, attached: !!opts.attachments }));
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }));
  }
}
