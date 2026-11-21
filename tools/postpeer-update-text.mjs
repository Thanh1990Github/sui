// cập nhật nội dung (tiêu đề, mô tả, tag, caption) của bài đã hẹn từ post.json, giữ video + giờ
import fs from "fs"; import path from "path";
const noLink = (t) => String(t || ""); // bài ngắn không có link (post-check đã kiểm)
const dir = process.argv[2];
const k = JSON.parse(fs.readFileSync("/root/.affiliate-video.json", "utf8")).POSTPEER_API_KEY;
const API = "https://api.postpeer.dev/v1", H = { "x-access-key": k, "Content-Type": "application/json" };
const j = async (m, p, b) => { const r = await fetch(API + p, { method: m, headers: H, body: b ? JSON.stringify(b) : undefined }); const t = await r.text(); let js = {}; try { js = JSON.parse(t) } catch {} return { s: r.status, js, t }; };
const post = JSON.parse(fs.readFileSync(path.join(dir, "post.json"), "utf8"));
const dang = JSON.parse(fs.readFileSync(path.join(dir, "dang.json"), "utf8"));
for (const [p, v] of Object.entries(dang.posts)) {
  const g = (await j("GET", "/posts/" + v.postId)).js.post;
  if (g.status !== "scheduled") { console.log(p, "skip", g.status); continue; }
  const body = JSON.parse(JSON.stringify(g.rawRequestBody));
  if (p === "youtube") {
    body.content = noLink(post.youtube.description);
    Object.assign(body.platforms[0].platformSpecificData, { title: post.youtube.title.slice(0, 100), tags: post.youtube.tags, firstComment: noLink(post.youtube.first_comment) });
  } else body.content = noLink(post[p].caption);
  const r = await j("PUT", "/posts/" + v.postId, body);
  const a = (await j("GET", "/posts/" + v.postId)).js.post;
  console.log(p, r.s, a.status, a.scheduledFor, "|", (a.rawRequestBody.platforms[0].platformSpecificData?.title || a.content).slice(0, 70));
}
console.log("usage", JSON.stringify((await j("GET", "/usage")).js.balance?.monthly?.remaining));
