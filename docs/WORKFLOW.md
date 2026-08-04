# Flow Chuẩn — Cắt/Sản Xuất Video

Living document. File này tiến hóa qua thực tế sử dụng: mỗi lần sản xuất kết thúc bằng **Post-Production Retro** (Stage 5), xác nhận flow này vẫn đủ hoặc sửa file này *trước khi* video được coi là xong. Không được bỏ qua bước check này.

Doc này sắp xếp thứ tự pipeline và định nghĩa các gate cứng. Không lặp lại nội dung rule đã có trong ADR hay `AGENTS.md` — chỉ cite theo số/tên để tránh lệch pha khi ADR thay đổi.

**Execution order thực tế:** `Stage -2 strategy/market selection → Stage -1A package
hypotheses → Stage 1 source + candidate discovery → Stage -1B payoff/critical lock
→ Stage 0 Hook Gate → Stage 2-7`. Tên `Stage 0` được giữ để không phá references hiện có; đây là blocking gate
chạy **sau khi đã có candidate span**, nhưng trước mọi cut/render/polish. Thứ tự
trình bày theo số stage không phải thứ tự gọi.

## Stage -2 — STRATEGY & MARKET SELECTION GATE (chặn cứng)

Mục đích của Stage -2 là trả lời **“có nên sản xuất video này không?”** trước khi
tối ưu câu hỏi “sản xuất nó đẹp thế nào?”. Đây là gate cấp hệ thống và luôn chạy
trước package, source download, TTS, asset search, EDL, renderer và QC.

### Pass 1 — Strategy role

1. Đọc active strategy của destination channel và ghi rõ asset role:
   `flagship`, `derivative_short`, `material_revision` hoặc `diagnostic_test`.
2. Với MONEY BLINDSPOT, active strategy là
   `docs/strategy/money-blindspot-longform-strategy-2026-07-28.md`: long-form là
   authority asset; Short mới phải là derivative của một flagship **đã publish**,
   có exact destination URL/Video ID và kế hoạch Related Video. Nếu flagship còn
   local-only hoặc Short không có destination, STOP.
3. Một task cục bộ như “làm video tiếp theo”, một source hấp dẫn hoặc một renderer
   có sẵn không được tự động override active strategy. Strategy change cần quyết
   định rõ của user; không được xảy ra ngầm trong production.

### Pass 2 — Idea portfolio, không phải một idea duy nhất

1. Tạo tối thiểu 10 lightweight ideas trước khi chọn source sâu. Mỗi idea chỉ cần:
   audience, familiar object/stakes, one-sentence gap, literal payoff, current
   attention wave, evergreen question và production feasibility sơ bộ.
2. Loại ngay idea yêu cầu cold viewer phải biết biography, company, luật chơi hoặc
   nhiều qualifier trước khi stakes có nghĩa. Unknown subject/company chỉ đủ điều
   kiện nếu opening gắn nó với một familiar anchor hoặc physical consequence nhìn
   thấy ngay; caption/UI không được thay thế object thật.
3. Chọn top 3 để tạo package hypotheses nhẹ. Chỉ 1 concept được đi tiếp vào Stage
   -1A/deep research. Mục tiêu là tăng số idea được falsify với chi phí thấp, không
   tăng số full render.

### Pass 3 — External demand proof

Mỗi concept muốn đi tiếp phải có evidence packet, không chỉ weighted score:

1. **Current-attention pool:** ít nhất 2 tín hiệu độc lập và có link/snapshot cụ thể
   cho thấy chủ đề đang có người quan tâm; source long-form có nhiều view không tự
   động chứng minh demand của một segment nằm sâu trong video đó.
2. **Evergreen human/business question:** một câu hỏi có giá trị kể cả khi current
   wave biến mất. MONEY BLINDSPOT dùng Topic Gate `>=75/100`, nhưng điểm này chỉ là
   prioritization floor, không phải market validation.
3. **Proven format mechanics:** tối thiểu 3 public winners đạt `>=1M` views, thuộc
   ít nhất 2 channel độc lập, chứng minh narrative/packaging mechanism có thể scale.
   Không cần copy exact topic; phải copy được causal engine như challenge, visible
   transformation, evidence pendulum, attempt ladder hoặc quantified comparison.
4. **Blue-ocean wedge:** viết một câu `competitors usually X; we create Y` trong đó
   Y tăng utility cho viewer, không chỉ thêm effect, caption, SFX hoặc production
   complexity.
5. **Destination fit:** giải thích vì sao đúng audience/channel này muốn xem và
   hành động tiếp theo sau Short là gì. “Có thể viral” không phải destination fit.

### Resource rule trước khi Stage -2 pass

- Được phép: web/YouTube research, transcript sampling, vài frame/source sample,
  title/frame-0 sketches và rough-hook cực nhẹ để kiểm tra feasibility.
- Không được phép: full source download nếu chỉ để khám phá mù, TTS final, Pexels
  sourcing, full EDL, SFX ledger, renderer, full MP4, Codex score loop hoặc upload.
- Internal hook score, editorial score, QC pass và creator/agent confidence không
  thể bù cho một market-evidence item còn thiếu.

**GATE RULE:** thiếu strategy fit, published destination (khi strategy yêu cầu),
idea tournament, current + evergreen demand, proven-format evidence hoặc blue-ocean
wedge thì STOP. Candidate quay lại idea portfolio; không được “cho production thử
rồi để analytics trả lời”. Analytics dùng để học từ một hypothesis đủ điều kiện,
không dùng để trả tiền cho lỗi selection có thể phát hiện trước production.

## Stage -1 — EXPECTATION & PAYOFF CONTRACT (chặn cứng)

Áp dụng trước Hook Gate theo hệ thống chuyển thể từ
[`guides/mrbeast-short-form-production-system.md`](guides/mrbeast-short-form-production-system.md):
không thể dựng đúng opening nếu chưa biết viewer được hứa điều gì và ending sẽ
trả bằng evidence nào (ADR-0037).

Stage -1 chạy hai pass: **A** tạo package/payoff hypotheses nhẹ trước download;
**B** chạy sau Stage 1 để thay mọi assumption bằng exact source/artifact, khóa
critical components và mới áp dụng blocking gate. Không gọi hypothesis của pass A
là verified proof.

0. Trước download/polish, tạo 3 lightweight candidate packages; mỗi candidate chỉ
   gồm working title/promise, frame-0 concept, progression engine, exact payoff và
   source/proof feasibility. Loại candidate false/unverifiable/infeasible; MAB chọn
   giữa các treatment đủ điều kiện, không để editor chọn tay theo sở thích.
1. Viết một câu `Audience + visible objective/stakes + unresolved question` mà
   cold viewer hiểu không cần title/description.
2. Chốt **payoff cuối** và artifact/source beat chứng minh payoff đó. Payoff yếu,
   không có quyền dùng, không verify được hoặc không trả đúng hook thì concept fail
   trước production polish.
3. Lập `Expectation Contract` gồm draft title promise, frame-0 promise, first
   spoken/caption promise và lý do cả ba cùng dẫn đến một payoff. Đây là working
   contract, chưa phải canonical metadata của Stage 5.
4. Chọn một **progression engine** nhìn thấy được (challenge/bet, stair-step,
   attempt ladder, claim → counter-evidence → verdict, trade/value ladder) với
   3-5 state. Một chuỗi quote hay nhưng không cho thấy tiến gần payoff không pass.
5. Chỉ ra một **Signature Moment** factual và khó thay thế: source-native reveal,
   verified comparison, counter-evidence flip, causal data viz hoặc story-native
   interaction. “Nhiều effect hơn” không phải signature moment.
6. Predeclare layer đang test, các layer phải freeze, metric chính sau 48h và điều
   kiện falsify. MAB/lane vẫn quyết định treatment được xuất bản; Stage -1 không
   cho phép editor chọn tay biến thể thắng.

Items 0-4 và payoff/expectation truthfulness là blocking. Signature Moment là craft
hypothesis bắt buộc phải khai báo (`declared` hoặc `none found`), không phải lý do để
bịa spectacle hay làm yếu một payoff vốn đã rõ. Exact timing/cut-rate vẫn là experiment
hypothesis dưới ADR-0036, không được nâng thành luật chỉ từ tài liệu MrBeast.

**GATE RULE (pass B):** thiếu exact payoff proof, critical component còn unverified,
progression engine không có causal state, hoặc expectation contract không khớp thì
STOP. Không được dùng hook cực đoan để bù cho một body/payoff chưa tồn tại.

## Stage 0 — 0–3s HOOK GATE (chặn cứng)

Chạy bước này trên MỌI candidate segment trước khi cắt, render, hoặc làm overlay. Không bước nào dưới đây được bắt đầu trước khi có 1 candidate pass.

```
1. Frame-0 face/action check (ADR-0017): tại t=0 candidate phải có mặt người
   hoặc hành động/prop rõ ràng — không phải title card, static text, hay B-roll.
   Check bằng mắt (visual inspection thủ công), không dùng script. Nếu nguồn có
   cả 2 lựa chọn, ưu tiên shot cận/tight (mặt chiếm phần lớn khung hình) hơn
   wide/establishing shot — mặt lớn hơn, rõ hơn, "đọc" nhanh hơn là có người
   đang nói chuyện với mình (aiwork v2: tight portrait mở đầu > v1's wide stage
   shot cho cùng Hook Gate item 1).
2. Gap-not-resolved check (CONTEXT.md → Hook): hook line dự kiến, đọc riêng,
   KHÔNG được nói hết toàn bộ claim — phải mở 1 gap/mystery ở 0-2s, chỉ
   partial reveal ở 5-8s.
3. Cause+effect co-naming check (AGENTS.md pitfall): headline không được nêu cả nguyên nhân VÀ hệ quả cụ thể cùng lúc.
4. Cadence feasibility (ADR-0018/0036): trong final 0-5s phải có phương án đạt
   target 1 Visual Change mỗi 0.8-1.5s; final 5-10s không có gap không giải thích
   >3s. Cut, reframe/zoom, overlay, đổi layout/source hoặc motion liên tục đều
   được tính; không ép hard cut làm hỏng câu thoại.
5. Guide-derived promise check (ADR-0034): trong 0-3s phải có cả visual surprise
   lẫn narrative promise rõ ràng; early SFX phải có slot trong t=0-1s và focal
   target phải đọc được ngay hoặc có thể chỉ bằng arrow/pointer/annotation.
6. Naive-viewer check (strengthened): cho một người không tham gia edit xem rough hook 0-3s mà không giải thích trước; họ phải nói được (a) exact object/person/action nhìn thấy mà không cần title/description, (b) open question/promise khiến họ muốn xem tiếp, và (c) họ kỳ vọng video sẽ chứng minh điều gì đến cuối. Nếu chỉ hiểu sau khi creator giải thích, hoặc chỉ hiểu sau khi đọc title/description, hoặc nếu object promised không visible trong final crop, hook fail. Production doc phải lưu ngày check, rough-hook version và câu trả lời nguyên văn đã ẩn danh cho cả ba câu hỏi; creator/agent tự xem không được tính là naive viewer. Không có evidence này thì item 6 là `unverified` và Hook Gate vẫn block render/upload — không được tự suy ra pass từ frame-check, caption timing hay cadence. Overlay-parroting (lặp lại headline bằng caption mà không có visible evidence cho object đã hứa) không pass item này.
7. Information Progression feasibility (ADR-0036): chuỗi Visual Changes dự kiến
   phải đẩy ít nhất một question, causal step, contrast, proof state hoặc payoff;
   không được dùng toàn flash/emoji/zoom trang trí chỉ để đủ cadence.
8. Title/description/creator opacity check (knAPeKpTpoA): frame 0 plus first spoken clause independently expose promised object/stakes or direct visual proof; caption alone cannot make vague pronouns (that/it/this) recognizable; if object not visible in final crop, change shot/span or proof-native opening.
```

**GATE RULE**: nếu bất kỳ item 1-8 trên MỌI candidate span trong source hiện tại, và không thể fix bằng cách chọn span khác trong cùng bản download, thì STOP. Quay lại Stage 1, chạy lại Stage -1B (payoff/critical lock) trước khi quay lại Stage 0. Không được tiến sang Stage 2/3/4, và không được ship 1 hook đã biết là yếu với lý do "để retention data trả lời sau."

## Stage 1 — Source Research & Candidate Selection

- Chọn Source Channel theo từng niche (ADR-0001/0004 finance, ADR-0019 health/VN, ADR-0020 AI-ed).
- Reverse-engineer outlier channels trước khi chốt treatment: copy narrative mechanics, pacing, hook/payoff và packaging đã chứng minh được demand; không copy topic execution, wording hay footage cụ thể của họ (ADR-0034).
- Stage 1 chỉ chạy cho concept đã pass Stage -2. Tại đây verify exact source span,
  visual object, escalation và literal payoff; không mở lại một concept đã bị
  Stage -2 loại chỉ vì tìm thấy quote hay hoặc source footage đẹp.
- Check `data/source_videos.csv` (source-video dedup registry) theo video ID/kênh trước khi chọn — tránh chọn lại đúng video hoặc lặp kịch bản đã dùng.
- Download max quality: `yt-dlp -f "bestvideo[height>=2160]+bestaudio"` (không bao giờ nhận default 720p — AGENTS.md).
- Transcribe (mlx_whisper).
- **Với nguồn dạng conference/talk dài (nhiều chục phút), trích 1 frame kiểm tra nhanh cho MỖI candidate window đã chọn từ transcript — không chỉ window của HOOK — trước khi chốt kế hoạch cắt**
- **Với nguồn rất dài (~1 giờ trở lên), đừng đọc/xem tuyến tính toàn bộ transcript để tìm candidate — keyword-scan trước.** Quét toàn bộ transcript bằng các từ khóa liên quan tới insight tổng quát hóa được (ví dụ: "question", "clarify", "the reason", "the point", "why", "important because") để khoanh vùng ứng viên, sau đó mới đọc kỹ + frame-check từng vùng đã khoanh (Stage 0 item 1, và note ở trên). Đọc tuyến tính không khả thi ở độ dài này (aiwork_v6: nguồn 4480s/74.6 phút, 599 segments — quét từ khóa tìm ra đúng 1 câu tổng quát hóa được, nằm ở phút 53:41 của một buổi livestream lập trình gần như toàn bộ là screen-share/jargon).
- Sau khi chốt source video dùng cho video mới, append 1 dòng vào `data/source_videos.csv`.
- Lưu source-use ledger theo **actual final timeline**, gồm duration của reused
  still frame; không cộng candidate windows chưa dùng và không bỏ qua still vì
  nó không phát audio. Mỗi stock asset phải có page URL, direct-file hash và
  provider-specific license marker. Chữ “free” trong page title không chứng minh
  commercial license; asset `restricted` phải bị loại hoặc giữ publication block.
- Audit các audio asset dự kiến qua shared SFX manifest của ADR-0038. Sound playable/downloadable trên MyInstants hoặc user-upload site chỉ là `reference_only` nếu chưa có independent commercial license; không đưa vào production pack vì tên file quen thuộc hay độ phổ biến.
- Lập **Critical Component ledger** cho mọi thứ mà thiếu nó thì không còn video
  trung thực: hook-capable moving shot, complete source-audio boundary, payoff/
  proof asset, license record, narration capability nếu cần, naive-viewer access và
  lane eligibility. Mỗi item ghi owner, evidence kiểm chứng, blocking state và
  backup; ưu tiên giải quyết critical path trước caption/effect polish.
- Ghi `Negatives / Failure modes` trước khi chốt source: rights mơ hồ, source quá
   yếu, quote thiếu vế, proof không đúng object, paid dependency, không có backup.
   "Tìm thấy asset" không đồng nghĩa asset usable; verify trực tiếp thay vì nhận
   metadata/vendor claim theo mặt chữ.

### Candidate Binary Prechecks (knAPeKpTpoA)

Trước mọi weighted scoring, chạy 5 binary prechecks trên mỗi candidate. Bất kỳ failure nào loại candidate ngay, không kể điểm weighted:

1. **Object visible in final vertical crop**: promised object/person/action phải nhìn thấy được trong crop 9:16 (1080x1920) mà không cần title/description.
2. **Stakes consequential to cold viewer**: stakes phải có ý nghĩa với người xem lạnh, không chỉ với người đã biết context.
3. **First payoff opens title larger loop**: payoff đầu tiên phải tạo ra một vòng lặp lớn hơn mà title hứa hẹn trả lời.
4. **Exact final payoff can begin partial resolution 3-8s**: payoff cuối phải bắt đầu partial resolution trong khoảng t=3-8s của final video.
5. **Naive-viewer access commitment**: candidate must commit to obtaining
   naive-viewer access for testing as a critical component before weighted
   scoring. The actual evidence collection and pass/fail determination occurs
   in Stage 0 item 6; Stage 1 precheck gates only whether that commitment is
   feasible. (knAPeKpTpoA)

Nếu bất kỳ precheck nào fail, candidate bị loại. Không được dùng weighted score để bù cho một precheck fail.

## Stage 2 — Cut Segment

- Extract candidate đã pass Stage 0. Chọn 1 trong 2 sub-format của Clip Curation Edit (ADR-0022):
  - **Contiguous VO** (sibling pattern được ADR-0022 cite qua ADR-0013): giữ nguyên
    trật tự/continuity của chosen source speech span trong khi visual crop, proof panel
    hoặc silent illustrative layer có thể thay đổi; dùng khi một source window có thể
    mang trọn hook → causal chain → payoff mà không phải đảo speech order.
  - **Multi-Clip Mashup** (ADR-0022, duration superseded by ADR-0034): nhiều đoạn rời rạc (mỗi đoạn <15s theo ADR-0007 item 3), nối bằng ffmpeg concat demuxer — dùng khi các moment mạnh nhất nằm rải rác quá xa nhau để gom vào 1 cửa sổ 50-75s duy nhất. Vẫn phải đạt tổng 50-75s sau khi ghép; audio joins vẫn phải pass Stage 4 fade/clarity gate.
- Production doc phải nêu rõ đang dùng sub-format nào (ADR-0022) trong phần "Why This Segment".
- Trước khi khóa EDL, map mỗi retained span vào một state của progression engine
  đã chốt ở Stage -1. Mỗi state phải đổi knowledge, stakes, causal step, evidence
  hoặc verdict; span chỉ lặp lại cùng ý phải rút ngắn hoặc bỏ.
- Rough-cut riêng **hook → first execution/proof → payoff** trước khi trang trí body.
  Sau khi mở loop, chuyển từ hype sang action/evidence sớm (thường khoảng 3-8s,
  nhưng ưu tiên semantic timing hơn fixed timestamp). Nếu ba anchor này không tạo
  cùng một causal chain, quay lại source/segment selection.
- Đặt Signature Moment tại nơi investment có nguy cơ phẳng, không dồn vào outro
  sau khi payoff đã xong. Ưu tiên creativity-first: authentic source/crop/timing →
  local data viz/animation → honest stock → paid generation sau explicit approval.

## Stage 3 — Hook Text + Overlays

- Viết hook overlay/caption/value-add. Phải thỏa ADR-0018 (caption sync), ADR-0036 (tiered cadence + Information Progression), ADR-0008 (Value-Add Layer).
- Nếu là Clip Curation Edit: phải thỏa thêm Transformative Gate của ADR-0007 (commentary track + ≥2 value-add + ≤50% source duration / mỗi clip <15s).
- Apply ADR-0034's `Caption Style Profile`: 2-5 từ/burst, một keyword animate/emphasize, tâm caption mặc định ở 55-65% chiều cao frame; chỉ dịch để tránh che face/proof sau visual review. English dùng Komika Axis, Vietnamese dùng Bangers; lấy thông số ffmpeg từ calibration artifact đã verify, không copy literal CapCut size 16/stroke 60.
- **Narrator Profile Gate (ADR-0039):** mọi Synthetic Narration English mới phải resolve machine-readable pointer `data/narrator-voices/default.json` tới `ronald_wayne_zack_style_qwen`, verify profile/reference/model hashes và dùng bound Rubber Band `<=1.42x`. Profile này chỉ dùng cho internal draft/review cho tới khi có explicit narrator consent/license; production doc phải giữ commercial publication block và disclosure rằng Zack D. Films không tham gia/endorse. Không silent fallback sang Edge TTS.
- Chạy **ADR-0038 Sonic Intent + SFX Event Ledger pass trước khi search/download**: lock vertical/tone/emotional states/default palette/excluded families; marker toàn bộ visible/implied event từ exact EDL; mỗi row ghi timestamp/pre-lap, trigger, story job, family/role, desired weight/mood, functional English search query, asset ID/gain/rights và full-mix verdict. Dùng template `docs/templates/sfx-event-ledger.md` trong production doc.
- Classify cue thành `diegetic_foley`, `motion_transition`, `state_emphasis` hoặc `tension_context`; `meme_voice_reference` bị quarantine nếu thiếu independent commercial rights, audience/language fit hoặc vertical credibility. Search bằng role + speed/weight/material/space/intensity thay vì ép một generic `whoosh`/`cash` vào mọi beat.
- Thêm một early SFX trong t=0-1s, nhưng cue phải có story job cụ thể. Nếu focal target không rõ ngay, thêm arrow/pointer/animated annotation; không thêm pointer trang trí khi target đã hiển nhiên.
- Mọi image entrance/exit hoặc transition đã chọn phải có mục đích kể chuyện và matching SFX; generic transition spam fail gate. Layer chỉ khi từng layer có job khác nhau: physical anchor, perceptual sweetener hoặc context.
- Bind SFX vào visible/implied event cụ thể; constant effect bed không đạt ADR-0036. `ambience` là contextual information; `drone`/`riser` có thể giữ một emotional state có lý do nhưng không thay thế event SFX. Narrative Short có Problem → Discovery → Payoff phải dùng các score state khác nhau và một music attenuation ngắn trước discovery/payoff quyết định; educational Short dùng section-level audio contrast, không bị ép vào arc ba trạng thái.
- Stock/Pexels phải ghi `ILLUSTRATION` khi reasonable viewer có thể nhầm đó là footage thật của người, sự kiện, sản phẩm hoặc evidence đang được claim. Generic b-roll hiển nhiên không bắt buộc label nhưng không được gọi là proof.
- Dựng custom on-brand CTA bumper bắt đầu trong t=38-42s, lời CTA nói rõ cả Like + Subscribe + Comment. Generic stock CTA template fail.
- Thêm moving watermark không che face/proof/caption và thay đổi vị trí theo timeline để chống crop đơn giản.
- **Hook text overlay tự thêm (không phải caption gốc của nguồn) phải xuất hiện gần như ngay lập tức (~t=0.1-0.2s, không trễ hơn) và cỡ chữ đủ lớn/màu đủ nổi bật để giữ chân người xem ngay từ đầu** (user feedback, hardknocks_v2: bản render đầu tiên delay hook overlay tới t=1.3s với size=36 để tạo cadence beat - quá nhỏ, quá trễ. Cadence (item 4, Stage 0) nên đạt bằng zoompan/motion liên tục hoặc cắt cảnh, KHÔNG phải bằng cách trì hoãn hook text). Tham khảo size ~48-52px ở khung 1080px-rộng là **mốc tối thiểu (floor), không phải mục tiêu (target)** cho hook text chính - hardknocks_v2 nhận feedback tăng size 4 lần liên tiếp trên cùng 1 video (36→52→64→80→84), ưu tiên to hơn khi khung hình còn chỗ, áp dụng cho cả text phụ (stat card/counter-argument/CTA), không chỉ hook chính.
- **Nếu tăng size sẽ khiến chữ bị crop ở mép 1080px, rút ngắn nội dung chữ trước, không coi size hiện tại là trần cố định** (hardknocks_v2: câu hook dài "OTHERS SAY MONEY = HAPPY..." đã chạy sát mép ở size=64, không thể tăng thêm nếu giữ nguyên độ dài - phải rút ngắn còn "OTHERS: MONEY = HAPPY" mới tăng lên size=80 được).
- **Mỗi lần tăng size phải tự verify lại bằng frame extraction thực tế, không được suy ra an toàn từ margin của lần tăng trước** (hardknocks_v2 vòng 4: rút ngắn chữ thêm + tăng size 80→90 trong 1 bước tưởng là an toàn theo ước tính số ký tự, nhưng frame check phát hiện chữ bị crop cả 2 mép - phải lùi về size=84 mới đạt). Rút ngắn chữ + tăng size cùng lúc có thể cộng dồn vượt ngưỡng dù mỗi thay đổi riêng lẻ trông hợp lý - luôn re-verify bằng Stage 4 self-check sau MỖI lần đổi size, không chỉ lần đầu tiên đổi.
- **Đo pixel width thực tế trước khi render, không chỉ sau khi render** (bacsihai_v7): trước khi commit 1 size vào render script cho BẤT KỲ drawtext overlay nào (hook text chính, stat card, header, CTA), đo thử bằng `PIL.ImageFont.getlength(text)` với đúng font file/size sẽ dùng, so với chiều rộng khung hình (1080px) trừ margin mong muốn. bacsihai_v7's header overlay ("NHIỀU NGƯỜI NGHĨ: CHOLESTEROL = XẤU" @ size 64) bị tràn khung ở lần render đầu - bắt được qua Stage 4 frame check (đúng như quy trình), nhưng đo trước bằng PIL sẽ bắt được ngay từ đầu, biến việc sửa thành 1 vòng thay vì nhiều vòng thử-sai như hardknocks_v2's 4 rounds. Bước đo pixel không thay thế frame-check bắt buộc sau khi render (vẫn phải làm), chỉ giảm số vòng lặp cần thiết.

## Stage 4 — Render & Spec Verify

- Chạy `pipeline/<project>/render_*.py`.
- Verify 9:16 (1080x1920), 50-75s, H.264, có audio stream — trước khi qua bước tiếp (ADR-0034).
- **Chính sách kiểm tra renderer: không viết unit test cho `render_*.py`.** Đây là repository sản xuất media; các renderer Python hiện tại là công cụ dựng video theo từng project, không phải product code cần TDD/test coverage.
- **Visual self-check bắt buộc**: trích xuất frame tại nhiều mốc trong cửa sổ hook (0-3s) và xem trực tiếp (không chỉ tin vào code) — xác nhận hook text overlay tự thêm hiển thị đúng thời điểm (~t=0.1-0.2s), đủ lớn/đủ nổi bật, không bị đè/che bởi caption gốc của nguồn; visual surprise + narrative promise đọc được; early SFX/focal annotation sync đúng beat. Nếu không đạt, sửa lại trước khi coi Stage 4 là xong — không lùi việc này sang Post-Production Retro.
- **Cadence + Information Progression check (ADR-0036)**: xem fixed frames/contact sheet ở 0.5-1s cadence xuyên final 0-10s và targeted body spans. Final 0-5s target Visual Change mỗi 0.8-1.5s; final 5-10s không có unexplained gap >3s; sau 10s không có unexplained gap >6s. Scene detector chỉ là advisory. Manual review phải xác nhận mỗi narrative phase có question/causal/proof/payoff progression, không chỉ effect spam.
- **Loop-Payoff Closure check (ADR-0036)**: đọc lại hook và ending cạnh nhau; ending phải trả đúng open loop ban đầu và không mở một lesson thứ hai mà Short chưa giải thích.
- **Expectation Match check**: đọc draft title promise, frame 0, first spoken/
  caption clause và final payoff cạnh nhau. Chúng phải mô tả cùng subject, stakes
  và causal story; hook tốt nhưng hứa một video khác vẫn fail.
- **No-Dull-Moment audit**: gán một job cho từng timeline interval: open/sharpen
  question, causal progress, stake increase, proof, verdict flip, setup payoff,
  payoff hoặc deliberate breathing room trước reveal. Interval không có job phải
  cut/shorten/replace. Purposeful silence có thể pass; decorative motion đơn thuần
  không pass dù cadence counter đạt. Bắt buộc xem toàn bộ exact-final artifact ở 1x,
  không suy ra pass chỉ từ contact sheet hoặc targeted body spans.
- **Abrupt-payoff safety**: kết thúc ngay sau payoff thay vì thêm outro/lesson mới,
  nhưng phải giữ complete meaning, evidence readability, audio decay và measured
  post-word margin. “Abrupt” không cho phép chặt phoneme hoặc final causal step.
- **Spoken-TTS preflight bắt buộc trước full render**: synthesize toàn bộ line riêng, đo raw/fitted duration và lưu per-line report (`voice`, engine rate/pitch, post-tempo, target duration, truncation). Không dùng `atempo < 1.0` để kéo chậm giọng lấp visual slot — giữ tốc độ tự nhiên rồi pad silence ở đuôi; nếu line quá dài thì rút gọn copy hoặc tăng nhẹ engine rate, chỉ cho phép post speed-up có bound. Ghép narrator-only preview và transcribe để bắt lỗi nuốt chữ/phát âm trước khi mix nhạc/source audio. Với TTS qua `loudnorm`, fit duration ở sample domain sau resample; xem pitfall chi tiết trong skill `clip-curation-edit`. (Root cause `trademe_v1`: macOS TTS có 5/9 line bị kéo xuống 0.72x, pass codec/loudness nhưng nghe phẳng và thiếu sức sống.)
- **Voice/TTS replacement sync gate**: khi thay voice hoặc TTS engine cho timeline đã dựng, slot-fit và tổng duration đúng KHÔNG chứng minh caption/visual sync. Render voice-control trước, transcribe audio của final MP4 bằng word timestamps, quantize `caption_at` lên frame kế tiếp, remap semantic visual theo clause thực sự được nói, và giữ caption layer tách khỏi static chrome. Với visual-only revision, mux lại accepted audio bằng stream copy và chứng minh audio-stream hash giống control. Bắt buộc có contact sheet toàn timeline + cặp BEFORE/AFTER quanh reveal; direct-source accurate seek phải reset PTS trước local caption gate. Xem `shorts-render-patterns/references/qwen-cloned-voice-word-sync-and-publishing.md` (root cause: Ronald Wayne v2 pass duration/ASR nhưng caption và proof visual chạy trước Qwen; v3 phát hiện thêm output-seek PTS bug ở direct quote).
- **Semantic source-frame gate**: word-aligned source window vẫn có thể mở vào
  người/phần chuyển cảnh thay vì object được caption. Với mỗi proof insert, trích
  exact frame tại planned in-point và ít nhất một frame sau đó; sửa seek nếu
  object không rõ. (Root cause: paperclip generator source `29.0s` → `30.8s`.)
- **Low-level ASR tail gate**: không caption hoặc coi mọi Whisper tail token là
  speech. Nếu tail nằm trên music bed, kiểm waveform và token repetition. Chỉ
  classify hallucination khi bed ở mức thấp đã định, một token chiếm phần lớn
  tail và deterministic narration mix không có speech trong window; tail words
  đa dạng vẫn phải fail/listen. (Root cause: repeated `Chaewoo` on paperclip v1.)
- **Checklist bắt buộc trước khi coi Stage 4 là xong** (mỗi mục dưới đây từng là 1 lỗi thật lọt qua `validate()`/decode pass — codec/spec pass KHÔNG có nghĩa là video sạch):
  - [ ] **Guide-derived craft + ADR-0038 SFX gate pass trên artifact cuối**: early SFX nghe được trong t=0-1s và map đúng ledger story job; 0-3s có visual surprise + narrative promise; focal pointer có mặt nếu cần; caption đúng font/profile, 2-5 từ/burst, keyword animate/emphasize, đọc được ở mobile preview và không che face/proof; CTA bumper custom bắt đầu t=38-42s và nói đủ Like/Subscribe/Comment; moving watermark thật sự đổi vị trí; transition/image motion có matching SFX. Nghe trong exact dialogue + music mix, xác nhận critical words không bị mask, intentional pre-lap đúng, không delayed cue nào rebase về t=0, repeated motif không gây fatigue, và mọi asset ID resolve tới publishable rights trong manifest. Kiểm waveform + frame/contact-sheet ở đúng timestamp, không chỉ đọc filter graph.
  - [ ] **Không có khoảng đen/dead space ở BẤT KỲ đoạn nào, không chỉ đoạn cuối.** Scan pixel dòng dưới cùng khung hình (`img[y].mean()` cho các y gần đáy) tại nhiều mốc thời gian rải suốt cả video — một dải đen cố định (ví dụ drawbox che caption gốc) có thể tồn tại xuyên suốt toàn video mà chỉ lộ rõ ở đoạn không có gì vẽ đè lên (thường là đoạn cuối). `blackdetect` chỉ bắt khung hình đen HOÀN TOÀN, không bắt một dải đen cục bộ trong khung hình còn lại có nội dung — phải tự scan pixel, không dựa `blackdetect` là đủ. Nếu có card/overlay che một phần khung hình, xác nhận có cần blackout hay không: chỉ blackout khi ĐÚNG là để che nội dung nguồn không kiểm soát được (caption gốc, logo…) — nếu không có gì vẽ đè lên sau đó, đừng vẽ đen, hãy crop bỏ + zoom lại (crop cả 2 chiều theo cùng hệ số, không riêng 1 chiều, để tránh méo hình).
  - [ ] **Tại mỗi điểm nối giữa 2 đoạn cắt (segment hard-cut), audio không được dừng/bắt đầu đột ngột ở full volume.** Scan `volumedetect` theo lát 0.1s, trải ~0.6s trước và sau MỖI điểm cắt — phải thấy 1 đường cong giảm dần xuống gần im lặng ngay tại điểm cắt rồi tăng dần trở lại (fade-out/fade-in), không phải một bước nhảy đột ngột từ full volume này sang full volume khác. Nếu đoạn cắt nào audio giữ nguyên full volume tới sát mép rồi nhảy thẳng sang đoạn kế, tiếng cuối câu sẽ nghe như bị chặt cụt/không rõ và cảm giác 2 câu "đè" lên nhau, không có khoảng nghỉ. Fix: thêm `afade=t=out` cuối mỗi đoạn + `afade=t=in` đầu mỗi đoạn khi render segment riêng lẻ (trước khi concat) — chỉ đổi biên độ, không đổi thời lượng/timing nên video vẫn giữ đồng bộ.
  - Chi tiết root-cause + số liệu thực tế của các lỗi trên: xem `docs/agent/media-pitfalls.md` (mục hardknocks b1/ruiz) và `docs/production/hardknocks-b1-ruiz-billionaire-check.md` (Revision 3, 4, và 5).

### Codex Media Review Loop (blocking before handoff)

Sau khi toàn bộ exact-final QC ở trên pass, chạy ADR-0040:

1. Tạo review packet mới từ đúng final MP4: 0-10s/full contact sheets, final ASR, timeline, loudness/spec/detector report, production contract và prior-round findings.
2. Gọi Codex ở read-only mode với `codex -a never exec --ephemeral -s read-only --output-schema docs/templates/codex-media-review.schema.json ...` và prompt từ `docs/templates/codex-media-review-prompt.md`. Lưu ý `-a never` là global option nên phải đứng trước `exec` trên Codex CLI hiện tại. Review phải cite timestamp/evidence và tối đa three actionable changes; không chấp nhận feedback chung chung như "thêm effect".
3. Nếu `editorial_score < 98`, chỉ apply finding có evidence, regenerate/rerender, chạy lại toàn bộ media QC, rebuild packet và xin review mới. Không rescore artifact cũ. Block editorial pass chỉ khi `blocked_external` đã được ghi nhận; một blocking media defect (missing SFX, black band, audio gap, caption mis-sync, v.v.) không phải editorial pass — phải fix trước khi xin review lại.
4. Dừng khi score `>=98` hoặc `blocked_external`; tối đa ba full rerender rounds. Round 3 vẫn dưới 98 mà không có external blocker thì ghi lesson, web-research case study/expert tương tự và tạo material revision mới với đúng một strategy change. Yêu cầu "stop optimizing" mà không có external blocker = STOPPED BELOW GATE, không phải completed.
5. Handoff chỉ là draft; không upload. Mọi upload dưới gate (editorial_score <98 mà không có blocked_external) phải liệt kê rõ từng failed gate và exact artifact hash (SHA-256) làm exception. Required below-gate discipline: do not attribute body/CTA/payoff to local final without passing exact-public-master verification. (knAPeKpTpoA)

`98` là internal editorial target, không phải dự báo hoặc bảo đảm triệu view. Score không override Hook/Transformative/rights/lane gates hoặc 48-hour metrics rule.

## Stage 5 — Document & Retro (`docs/production/<name>.md`)

Điền theo template hiện có (Status, Video Specs, YouTube Title/Description, Source, Why This Segment, Hook Formula Applied, Value-Adds, **Sonic Intent + SFX Event Ledger**, Known Issues, What to Check at 48h) — dùng `docs/templates/sfx-event-ledger.md` cho audio và xem `docs/production/bacsihai-v5-lao-dong-tay.md` làm mẫu chung.

### Hook Gate Evidence (blocking)

Production doc phải ghi riêng evidence của Stage 0 item 6: ngày check, định danh
rough-hook version, câu hỏi đưa cho naive viewer (không được giải thích story) và
câu trả lời nguyên văn đã ẩn danh về (a) họ thấy chuyện gì đang xảy ra, (b) open
question/stakes là gì, (c) họ có tiếp tục xem không và vì sao. Dòng tự đánh giá
kiểu "frame-0 pass" / "hook mạnh" không thay thế evidence này. Thiếu section này
thì Status không được chuyển thành `Completed` và Short không được upload.

### Publishing Metadata & Studio Settings Gate (blocking)

Trước khi chuyển production doc sang trạng thái sẵn sàng upload (pre-upload), chạy packaging workflow rồi lưu đúng một canonical upload package:

1. Trích `central decision/object`, stakes, open loop, known audience anchor và factual constraints từ final script/artifact.
2. Tạo ít nhất 5 title thuộc các family money/number, decision, contradiction, authority và question; chấm từng title theo cold-viewer clarity, stakes, open loop, factual accuracy và mobile-length compliance. Với cold audience, ưu tiên object/entity đã biết hơn proper name ít người biết. Claim đang tranh cãi phải ở dạng question hoặc attribution, không được biến thành fact.
3. Chọn đúng một canonical title; không đưa alternatives vào upload package. Sau đó tạo description và Studio fields theo gate dưới đây.

Canonical upload package phải đủ các trường sau:

1. `Title`: một title đã chọn, không còn alternatives; tối đa 30 user-visible characters gồm spaces/emoji, Title Case ở mọi vertical, đúng hai emoji phù hợp.
2. `Description`: dòng đầu mirror Title; tối đa một câu mô tả bổ sung, giữ rõ ranh giới giữa fact độc lập và source-reported claim, không chứa raw affiliate link; cuối description là đúng ba Hashtags.
3. `Hashtags`: đúng ba hashtag liên quan, bắt buộc chứa `#shorts`, không hashtag soup.
4. `YouTube Studio Tags`: đúng ba niche-specific tags, là field riêng và không thay thế Hashtags.
5. `Audience`: `Not made for kids` cho ba vertical hiện tại; nếu nội dung tương lai thực sự directed at children thì legal classification override default này.
6. `Video Language`, `Location`, `Category`: ghi explicit, localized và chính xác.
7. `Playlist`: master playlist của đúng vertical.
8. `Related Video`: winner hiện tại sẽ được update để trỏ tới Short mới; first-upload bootstrap ghi `none — first channel upload`.
9. `Upload Details Template`: tên/ID template đã approve, dùng lại trong Studio.

Sau đó bắt buộc kết thúc mọi production doc bằng section này — yêu cầu MỌI lần, không chỉ khi có vấn đề:

```
## Post-Production Retro

### Hook Retro (bắt buộc, mọi video — proactive)
- Verbal: có cách nào làm hook lời nói/text mạnh hơn trong 3 giây đầu không?
  (Có ý tưởng mới? Viết ra. Không tìm được gì tốt hơn? Viết "none found.")
- Visual: có cách nào làm hook hình ảnh mạnh hơn trong 3 giây đầu không
  (framing, motion, prop, cut timing,...)? Áp dụng cùng rule.
- Nếu ý tưởng generalize được ra ngoài video này, cập nhật/thêm 1 item vào
  checklist Stage 0 trong docs/WORKFLOW.md ngay, cite video này làm nguồn.

### Workflow Delta (bắt buộc, mọi video — reactive)
Lần sản xuất này có gặp case mà các stage trong docs/WORKFLOW.md chưa cover không?
- Không -> viết "none".
- Có -> thực hiện đúng 1 hành động trước khi coi video này là xong:
  - Lỗ hổng về thứ tự/quy trình (rule đã tồn tại ở nơi khác, workflow chỉ
    chưa nói rõ khi nào check) -> sửa ngay stage tương ứng trong WORKFLOW.md.
  - Rule hoàn toàn mới, chưa từng được thiết lập -> viết ADR mới, rồi thêm
    1 dòng cite vào WORKFLOW.md.
  - Sự cố một lần, không phải rule chung -> thêm entry vào file phù hợp trong
    `docs/agent/` thay vì làm phình context luôn-nạp ở root `AGENTS.md`.

### MrBeast-System Retro (bắt buộc, mọi video)
- Expectation: title/frame-0/first line/payoff có còn cùng một promise trên exact
  final artifact không?
- Progression: state nào yếu hoặc lặp lại; Signature Moment có thật sự khó thay thế
  hay chỉ là effect?
- Critical path: bottleneck/component nào được phát hiện quá muộn; backup có hoạt
  động không?
- Dullness: interval nào không có story job; nếu giữ lại, lý do semantic là gì?
- Next test: nêu đúng một layer sẽ đổi, các layer freeze, metric thật sau 48h và
  falsification condition. Không gọi toàn bộ “MrBeast formula” thắng/thua từ một
  upload bundle.
```

### Post-Publish Retention Postmortem (blocking, mọi mature upload)

Mỗi upload đã mature (≥48h, đã có dữ liệu distribution) phải ghi đầy đủ các mục sau vào production doc trước khi Status được đánh dấu `Completed`:

1. `distribution_state`: Shorts Feed traffic share (≥70% / 60-<70% / <60%) và No-Feed State nếu applicable.
2. `public_master_identity`: exact file path, SHA-256, duration của artifact đã upload — phải khớp với exact-public-master gate đã ghi ở Stage 6.
3. `0-3s_result`: retention/response trong cửa sổ hook 0-3s.
4. `0-10s_result`: retention/response trong cửa sổ 0-10s.
5. `expectation_match`: title/frame-0/first-clause/payoff expectation có khớp nhau trên exact public artifact không.
6. `three_largest_retention_changes`: ba thay đổi retention lớn nhất, mỗi cái mapped về exact public EDL timestamp và story job đã predeclare.
7. `controlled_revision`: đúng một controlled change cho Short kế tiếp (falsification condition đi kèm).

Packaging workflow này kiểm soát chuyển sang trạng thái pre-upload (sẵn sàng upload); trạng thái `Completed` cuối cùng vẫn bị chặn cho tới khi đầy đủ yêu cầu post-production và post-publish retro.

**Enforcement**: Status KHÔNG được đánh dấu `Completed` cho tới khi mục này đã điền đầy đủ. Thiếu bất kỳ mục con nào => block completion và upload tiếp theo.

**Enforcement**: Status của production doc một video KHÔNG được đánh dấu done, và dòng của nó trong `docs/experiments/EXPERIMENT-LOG.md` KHÔNG được đánh dấu final, cho tới khi cả 3 subsection Post-Production Retro trên đã điền đầy đủ — dù chỉ là "none" / "none found" — VÀ mục Post-Publish Retention Postmortem đã điền đầy đủ.

## Stage 6 — Upload & Log

- **Exact-public-master gate (knAPeKpTpoA)**: trước khi chạy lane eligibility gate, record accepted file path, SHA-256, và duration của local final artifact. Sau khi upload, verify same file (matching SHA-256) được chọn trong Studio picker; preserve selection evidence. Sau publication download/probe public transcode, so sánh duration/opening ASR/timeline landmarks với local final; material mismatch => INVALID ARTIFACT MAPPING, stop và ghi nhận. Không attribute body/CTA/payoff cho local final trước khi exact public EDL mapping đã pass.
- **Lane eligibility gate (ADR-0035)**: xác nhận Destination Channel hiện tại đúng strict round-robin order và Short trước trên lane đó đã đạt Distribution Plateau. Nếu chưa, STOP/queue; không skip lane. Ngoại lệ duy nhất: Short đầu tiên trên channel vẫn viral thì Short thứ hai có thể lên sau khoảng bảy ngày.
- Upload thủ công. Không paste raw affiliate link trong description (dùng redirect domain). Set `Not made for kids`, language, location, category và master playlist.
- Sau upload, set/verify Related Video wiring: winner hiện tại → Short mới; first-upload bootstrap được miễn.
- Log dòng đầu tiên vào `docs/experiments/EXPERIMENT-LOG.md`.
- Trong 48h đầu, reply genuine questions/substantive comments để giữ thread hữu ích hoạt động; bỏ qua spam, abuse và engagement bait lặp lại.

## Stage 7 — 48h Distribution & Plateau Verification

0. Trước khi gọi một Short “creative flop”, tách distribution khỏi creative:
   - public views thấp hoặc `Shown in feed` quá nhỏ → creative inconclusive;
   - feed sample đủ + Stayed to watch thấp → 0-3s/hook hypothesis;
   - Stayed ổn + AVD/APV thấp → body/escalation hypothesis;
   - retention tốt + shares/comments yếu → payoff/identity hypothesis.
   Map retention timestamps về exact visual EDL. Không suy ra retention failure
   từ public view count hoặc thumbnail một mình.
1. Chờ đủ 48h rồi mới fetch/check; không panic hoặc xóa sớm trong pickup window 24-48h.
2. Record Shorts Feed traffic share:
   - `>=70%` → healthy;
   - `60%..<70%` → watch state, giữ và monitor;
   - `<60%` → No-Feed State.
3. No-Feed original luôn được giữ. Tạo Material Revision bằng cách dựng lại toàn bộ 0-3s (shot/framing + hook copy + early SFX) và đổi thêm ít nhất một axis trong pacing/cut order, proof visuals, captions hoặc music; metadata-only/music-only không tính. Queue revision vào lane kế tiếp khi eligible.
4. Ba No-Feed liên tiếp trên cùng lane → Channel Burn State; remove lane khỏi rotation trong lúc replacement được phone-verify và age ≥3 tuần. Một Short flop không đủ kết luận burn.
5. Mỗi 24h record view increment. Distribution Plateau chỉ pass khi latest 24h increment `<=20%` preceding 24h increment ở hai checks liên tiếp và Short đã ≥48h. Video vẫn kéo view/ngày cao/ổn định không phải plateau.
6. Khi plateau, inspect AVD và retention 0-3s; metric yếu nhất phải được ghi vào production brief của Short kế tiếp. Không dùng API AVD/APV để giả lập Studio Stayed to Watch.
7. Map mọi retention rise/drop đáng kể về exact EDL timestamp **và story job đã
    predeclare** ở Stage -1/4. Kết luận ở layer nhỏ nhất có evidence (expectation,
    hook mechanism, proof timing, progression, signature moment, CTA, payoff),
    không dùng nhãn chung "MrBeast editing fail". Public mismatch blocks causal
    body/CTA/payoff conclusions; high Swiped Away diagnoses opening only when
    opening parity holds; not narrator/CTA/body/sound/payoff by default. Failure
    phải đi tiếp thành: lesson → expert/case-study research → một strategy change
    → treatment kế tiếp khi lane eligible.
8. Mỗi `Post-Publish Retention Postmortem` phải ghi: distribution state; 0-3s và
   0-10s response; ba rise/drop lớn nhất gắn exact EDL/caption/SFX; vùng CTA
   t=38-42s; retention từ payoff onset tới EOF; expectation contract có được exact
   artifact giao đúng không; và đúng một controlled change cho Short kế tiếp. So
   sánh trong cùng lane/vertical ở mốc trưởng thành tương đương, không pool chín
   channel như một cohort vì channel history là confounder.
