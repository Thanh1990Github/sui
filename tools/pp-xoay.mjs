#!/usr/bin/env node
// Đăng qua PostPeer với NHIỀU key (nhiều tài khoản PostPeer): tự chọn key còn đủ lượt và đã kết nối đủ nền tảng.
// Key đọc từ ~/.affiliate-postpeer-keys.json  {"POSTPEER_KEYS": ["key1","key2","key3"]}  (không commit, không in ra).
//
//   node tools/pp-xoay.mjs xem                                   số lượt còn lại + kênh của từng key
//   node tools/pp-xoay.mjs dang <thư-mục-video> [--nen-tang youtube,tiktok] [--lich "YYYY-MM-DD HH:MM"] [--yes]
//
// Trước khi đăng thật (--yes) luôn chạy tools/check-trung.py; trùng tiêu đề/nội dung thì dừng.
// Mã kênh khác nhau theo từng tài khoản PostPeer, nên lệnh tạm ghi mã kênh của tài khoản được chọn vào
// kenh.json (mục "dang") rồi gọi pp.mjs của skill dang-video-v2, xong ghi số tài khoản vào dang.json ("tk").
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const KEYS = path.join(os.homedir(), ".affiliate-postpeer-keys.json");
const ONE = path.join(os.homedir(), ".affiliate-video.json");
const PP = "/root/.claude/skills/synced/6510cc56-1b79-4705-b6b4-0398ad97f2c1_fa644f3c-37bb-4faf-a9e1-ddfb0b2eb647/dang-video-v2/scripts/pp.mjs";
const API = "https://api.postpeer.dev/v1";
const die = (m) => { console.error("✗ " + m); process.exit(1); };
const rj = (f, d) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return d; } };

const keys = rj(KEYS, {}).POSTPEER_KEYS || die(`chưa có ${KEYS}`);
const get = async (k, p) => (await fetch(API + p, { headers: { "x-access-key": k } })).json();

async function info() {
  const out = [];
  for (const [i, k] of keys.entries()) {
    const u = await get(k, "/usage").catch(() => ({}));
    const it = await get(k, "/connect/integrations").catch(() => ({}));
    const acc = {};
    for (const x of it.integrations || it.data || []) acc[x.platform] = { id: x.id || x._id, name: x.displayName || x.name || "" };
    out.push({ tk: i + 1, k, left: u.balance?.monthly?.remaining ?? 0, used: u.balance?.monthly?.used ?? 0, acc });
  }
  return out;
}

const [cmd, ...args] = process.argv.slice(2);
if (cmd === "xem") {
  for (const a of await info()) console.log(`Key ${a.tk}: còn ${a.left} lượt (đã dùng ${a.used}) · ${Object.keys(a.acc).join(", ") || "chưa kết nối kênh"}`);
  process.exit(0);
}
if (cmd !== "dang") die("dùng: xem | dang <thư-mục-video> [--nen-tang …] [--lich …] [--yes]");

const vdir = args[0] || die("thiếu thư mục video");
const ni = args.indexOf("--nen-tang");
const long = /video-dai/.test(vdir) || rj(path.join(vdir, "plan.json"), {}).format === "long";
const want = ni >= 0 ? args[ni + 1].split(",") : long ? ["youtube", "facebook"] : ["youtube", "tiktok", "facebook", "instagram"];
const yes = args.includes("--yes");

if (yes) {
  const c = spawnSync("python3", ["tools/check-trung.py", "--dir", vdir], { stdio: "inherit" });
  if (c.status !== 0) die("kiểm trùng không qua → không đăng");
}

const all = await info();
const pick = all.find((a) => a.left >= want.length && want.every((p) => a.acc[p]));
if (!pick) die(`không key nào còn ≥ ${want.length} lượt và có đủ ${want.join(", ")}. Lượt còn: ${all.map((a) => `key ${a.tk}=${a.left}`).join(", ")}`);
console.log(`→ dùng key ${pick.tk} (còn ${pick.left} lượt)`);

// cài tạm key được chọn + mã kênh của tài khoản đó
const one = rj(ONE, {}); one.POSTPEER_API_KEY = pick.k; fs.writeFileSync(ONE, JSON.stringify(one, null, 2), { mode: 0o600 });
let kdir = path.resolve(vdir); while (!fs.existsSync(path.join(kdir, "kenh.json"))) { kdir = path.dirname(kdir); if (kdir === "/") die("không thấy kenh.json"); }
const kf = path.join(kdir, "kenh.json"), K = rj(kf, {}), backup = JSON.stringify(K.dang || {});
K.dang = { ...(K.dang || {}) };
for (const p of ["youtube", "tiktok", "facebook", "instagram"]) if (pick.acc[p]) K.dang[p] = { ...(K.dang[p] || {}), id: pick.acc[p].id, name: pick.acc[p].name }; else delete K.dang[p];
fs.writeFileSync(kf, JSON.stringify(K, null, 2));
const r = spawnSync(process.execPath, [PP, "dang", ...args], { stdio: "inherit", env: { ...process.env, NODE_USE_ENV_PROXY: "1" } });
// trả kenh.json về như cũ, ghi tài khoản đã dùng vào dang.json
const K2 = rj(kf, {}); K2.dang = JSON.parse(backup); fs.writeFileSync(kf, JSON.stringify(K2, null, 2));
const df = path.join(vdir, "dang.json");
if (yes && fs.existsSync(df)) { const d = rj(df, {}); for (const p of want) if (d.posts?.[p]) d.posts[p].tk = pick.tk; fs.writeFileSync(df, JSON.stringify(d, null, 2)); }
process.exit(r.status ?? 1);
