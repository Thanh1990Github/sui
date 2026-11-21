// node swap.mjs <video_dir> <platform,...>  : thay file video của bài đã hẹn giờ (giữ nội dung + giờ)
import fs from "fs"; import path from "path";
const [dir, plats] = process.argv.slice(2);
const k = JSON.parse(fs.readFileSync("/root/.affiliate-video.json", "utf8")).POSTPEER_API_KEY;
const API = "https://api.postpeer.dev/v1", H = { "x-access-key": k, "Content-Type": "application/json" };
const j = async (m, p, b) => { const r = await fetch(API + p, { method: m, headers: H, body: b ? JSON.stringify(b) : undefined }); const t = await r.text(); let js = {}; try { js = JSON.parse(t) } catch {} return { s: r.status, js, t }; };
const usage = async () => (await j("GET", "/usage")).js.balance?.monthly;
console.log("usage before", JSON.stringify(await usage()));
const up = await j("POST", "/media/upload", { filename: "video.mp4", mimeType: "video/mp4" });
const d = up.js.data; const buf = fs.readFileSync(path.join(dir, "video.mp4"));
const put = await fetch(d.uploadUrl, { method: "PUT", body: buf, headers: { "Content-Type": "video/mp4" } });
if (!put.ok) throw new Error("upload " + put.status);
const dang = JSON.parse(fs.readFileSync(path.join(dir, "dang.json"), "utf8"));
for (const p of plats.split(",")) {
  const id = dang.posts[p].postId; const g = (await j("GET", "/posts/" + id)).js.post;
  if (g.status !== "scheduled") { console.log(p, "skip status", g.status); continue; }
  const body = { ...g.rawRequestBody }; body.mediaItems = body.mediaItems.map((m) => ({ ...m, url: d.publicUrl }));
  const r = await j("PUT", "/posts/" + id, body);
  const a = (await j("GET", "/posts/" + id)).js.post;
  console.log(p, r.s, r.t.slice(0, 160).replace(/\n/g, " "), "| now:", a.status, a.scheduledFor, a.mediaItems[0].url === d.publicUrl ? "NEW_MEDIA" : "OLD_MEDIA");
}
dang.media_url = d.publicUrl; fs.writeFileSync(path.join(dir, "dang.json"), JSON.stringify(dang, null, 2));
console.log("usage after", JSON.stringify(await usage()));
