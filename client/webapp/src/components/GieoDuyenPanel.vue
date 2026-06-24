<template>
  <div class="gieo-duyen">
    <header class="gd-hero">
      <div class="gd-hero-icon">💞</div>
      <h2>Gieo Duyên</h2>
      <p class="gd-sub">Đạo phu thê soi qua ba hệ Đông phương — Tử Vi · Bát Tự · Kinh Dịch</p>
      <p class="gd-tag">Đúc kết sau khi đọc nhiều sách và tự phản biện · không bói toán, mệnh là động từ</p>
      <div class="gd-actions">
        <a class="gd-pdf-btn" href="/GIEO-DUYEN.pdf" target="_blank" rel="noopener">📄 Đọc / tải bản PDF</a>
      </div>
    </header>

    <!-- Chọn chế độ -->
    <div class="gd-mode">
      <button :class="{ on: mode === 'tim' }" @click="mode = 'tim'">🔍 Tôi đang tìm</button>
      <button :class="{ on: mode === 'cap' }" @click="mode = 'cap'">💑 Đã có đôi</button>
      <button :class="{ on: mode === 'so' }" @click="mode = 'so'">⚖️ So nhiều người</button>
      <button :class="{ on: mode === 'tinh' }" @click="mode = 'tinh'">💍 Tình duyên</button>
    </div>

    <!-- CHẾ ĐỘ ĐANG TÌM: 4 tính năng cho người độc thân -->
    <section v-if="mode === 'tim'" class="gd-tool">
      <h3>🔍 Duyên của tôi</h3>
      <p class="gd-tool-sub">Nhập lá số của bạn — hệ thống vẽ chân dung nửa kia, đọc đường tình duyên, chỉ năm có duyên và tuổi hợp.</p>
      <div class="gd-form">
        <div class="gd-person" style="flex:1">
          <input v-model="dn" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="db" type="datetime-local" class="gd-in" />
          <select v-model="dg" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
      </div>
      <button class="gd-run" :disabled="!db || dloading" @click="runDuyen">
        {{ dloading ? '⏳ Đang xem...' : '💗 Xem duyên của tôi' }}
      </button>
      <p v-if="derr" class="gd-err">{{ derr }}</p>

      <div v-if="dres" class="gd-result">
        <!-- Chân dung nửa kia -->
        <div class="gd-card">
          <h5>💗 Chân dung nửa kia</h5>
          <ul><li v-for="(m,i) in dres.chan_dung_nua_kia.mo_ta" :key="i">{{ m }}</li></ul>
          <p class="gd-mini">Con giáp dễ hợp:
            <b v-for="(g,i) in dres.chan_dung_nua_kia.con_giap_hop.tam_hop" :key="i">{{ g }} </b>
            <b v-if="dres.chan_dung_nua_kia.con_giap_hop.luc_hop">· {{ dres.chan_dung_nua_kia.con_giap_hop.luc_hop }}</b>
          </p>
          <p class="gd-note">{{ dres.chan_dung_nua_kia.loi_khuyen }}</p>
        </div>
        <!-- Đường tình duyên -->
        <div class="gd-card">
          <h5>🔍 Đường tình duyên — xu hướng: <b>{{ dres.duyen_ca_nhan.xu_huong }}</b></h5>
          <ul><li v-for="(t,i) in dres.duyen_ca_nhan.tin_hieu" :key="i">{{ t.noi_dung }}</li></ul>
          <p class="gd-mini">Cách vận hành (mệnh là động từ):</p>
          <ul class="gd-do"><li v-for="(c,i) in dres.duyen_ca_nhan.cach_van_hanh" :key="i">{{ c }}</li></ul>
        </div>
        <!-- Năm có duyên -->
        <div class="gd-card">
          <h5>📅 Năm có duyên ({{ dres.nam_co_duyen.tu_nam }}–{{ dres.nam_co_duyen.den_nam }})</h5>
          <div v-if="dres.nam_co_duyen.nam_co_duyen.length" class="gd-years">
            <span v-for="(y,i) in dres.nam_co_duyen.nam_co_duyen" :key="i" class="gd-year">
              <b>{{ y.nam }}</b> <small>({{ y.cung.join('/') }} · {{ y.sao }})</small>
            </span>
          </div>
          <p v-else class="gd-mini">Không có năm sao hỉ nổi bật trong 12 năm tới — duyên đến tự nhiên, chủ động vẫn hơn.</p>
          <p class="gd-note">{{ dres.nam_co_duyen.ghi_chu }}</p>
        </div>
        <!-- Tuổi hợp -->
        <div class="gd-card">
          <h5>🧭 Tuổi hợp – tuổi cần ý thức (bạn tuổi {{ dres.tuoi_hop.con_giap }})</h5>
          <div class="gd-tuoi">
            <span class="ok">Tam hợp: <b>{{ dres.tuoi_hop.tam_hop.map(x=>x.con_giap).join(', ') }}</b></span>
            <span class="ok">Lục hợp: <b>{{ dres.tuoi_hop.luc_hop.con_giap }}</b></span>
            <span class="warn">Xung: {{ dres.tuoi_hop.luc_xung.con_giap }}</span>
            <span class="warn">Hại: {{ dres.tuoi_hop.luc_hai.con_giap }}</span>
          </div>
          <p class="gd-note">{{ dres.tuoi_hop.ghi_chu }}</p>
        </div>
        <!-- Món 2: lời văn ấm -->
        <div class="gd-card gd-tho-card">
          <button v-if="!dtho && !dthoLoading" class="gd-soft-btn" @click="runDuyenTho">💌 Nghe lời tâm tình về duyên của bạn</button>
          <p v-if="dthoLoading" class="gd-mini">✍️ Thầy đang viết đôi lời...</p>
          <div v-if="dtho" class="gd-tho">{{ dtho }}</div>
        </div>
        <!-- Món 4: chia sẻ -->
        <div class="gd-share">
          <button class="gd-soft-btn" @click="shareCard('Chân dung nửa kia của tôi', dres.chan_dung_nua_kia.mo_ta[0]||'', 'Xu hướng: '+dres.duyen_ca_nhan.xu_huong, null)">📤 Tạo thẻ chia sẻ</button>
        </div>
        <p class="gd-para">⚖️ {{ dres.paradigm }}</p>
      </div>
    </section>

    <!-- CHẾ ĐỘ SO NHIỀU NGƯỜI -->
    <section v-if="mode === 'so'" class="gd-tool">
      <h3>⚖️ So nhiều người</h3>
      <p class="gd-tool-sub">Đang phân vân giữa vài người? Nhập lá số của bạn và của họ — hệ thống xếp hạng độ tương ứng.</p>
      <div class="gd-person" style="margin-bottom:12px;">
        <h4>Bạn</h4>
        <input v-model="soMe.ten" placeholder="Tên (tuỳ chọn)" class="gd-in" />
        <input v-model="soMe.birth" type="datetime-local" class="gd-in" />
        <select v-model="soMe.gender" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
      </div>
      <div v-for="(o,i) in soOthers" :key="i" class="gd-other-row">
        <input v-model="o.ten" :placeholder="'Người '+(i+1)" class="gd-in" style="flex:1" />
        <input v-model="o.birth" type="datetime-local" class="gd-in" style="flex:1.4" />
        <select v-model="o.gender" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        <button class="gd-x" @click="rmOther(i)" v-if="soOthers.length>1">✕</button>
      </div>
      <button class="gd-add" @click="addOther" v-if="soOthers.length<8">+ Thêm người</button>
      <button class="gd-run" :disabled="soLoading" @click="runSoSanh">{{ soLoading ? '⏳ Đang so...' : '⚖️ Xếp hạng' }}</button>
      <p v-if="soErr" class="gd-err">{{ soErr }}</p>
      <div v-if="soRes" class="gd-result">
        <div v-for="(r,i) in soRes.xep_hang" :key="i" class="gd-rank">
          <span class="gd-rank-no">{{ i+1 }}</span>
          <div class="gd-rank-body">
            <div class="gd-rank-top"><b>{{ r.ten }}</b> <span class="gd-rank-score">{{ r.diem_tong }}</span> <span v-if="r.ung_nhau" class="gd-ung">cương–nhu ứng ✓</span></div>
            <div class="gd-rank-muc">{{ r.muc }}</div>
            <div v-if="r.diem_noi_bat" class="gd-rank-k">🔑 {{ r.diem_noi_bat }}</div>
          </div>
        </div>
        <p class="gd-note">{{ soRes.ghi_chu }}</p>
      </div>
    </section>

    <!-- CHẾ ĐỘ TÌNH DUYÊN (nữ mệnh) — đọc đồng dạng trên lá số của chính bạn -->
    <section v-if="mode === 'tinh'" class="gd-tool">
      <h3>💍 Nữ mệnh — Tình duyên</h3>
      <p class="gd-tool-sub">
        Soi đường tình duyên trên <b>lá số của chính bạn</b> — hợp nhất Tử Vi và Bát Tự, đọc theo từng
        chặng đời. Mệnh là động từ: lá số cho biết <em>TÍNH</em> (nguyên liệu trời ban), còn cách
        <em>vận hành</em> là ở bạn — không bói cát/hung.
      </p>

      <div v-if="tdWho" class="gd-td-who">
        <span>Đọc cho: <b>{{ tdWho }}</b></span>
        <span v-if="tdBirth"> · sinh {{ tdBirth }}</span>
        <span v-if="tdGender"> · {{ tdGender }}</span>
      </div>

      <button class="gd-run" :disabled="tdLoading" @click="runTinhDuyen">
        {{ tdLoading ? '⏳ Đang soi tình duyên...' : '💗 Xem tình duyên (30 xu)' }}
      </button>
      <p v-if="tdErr" class="gd-err">{{ tdErr }}</p>

      <div v-if="tdRes" class="gd-result gd-td">
        <p v-if="tdRes.cached" class="gd-note">♻️ Lượt hỏi gần đây — không trừ xu lại (một việc một lần).</p>
        <p v-else-if="tdRes.charged_xu" class="gd-note">
          Đã dùng {{ tdRes.charged_xu }} xu<span v-if="tdRes.xu_balance != null"> · số dư: {{ tdRes.xu_balance }} xu</span>.
        </p>

        <!-- ⭐ KHỐI CHẨN ĐOÁN CẤP ĐỘ — tính năng KILLER, hiển thị đầu tiên -->
        <div v-if="tdRes.chan_doan_cap_do && tdRes.chan_doan_cap_do.cap_do" class="gd-card gd-cd">
          <div class="gd-cd-top">
            <span class="gd-cd-badge" :class="'lv-' + tdRes.chan_doan_cap_do.cap_do">
              Mức độ thử thách {{ tdRes.chan_doan_cap_do.cap_do }}/5
              <b v-if="tdRes.chan_doan_cap_do.ten_cap"> — {{ tdRes.chan_doan_cap_do.ten_cap }}</b>
            </span>
            <div class="gd-cd-dots" :aria-label="'Cấp ' + tdRes.chan_doan_cap_do.cap_do + ' trên 5'">
              <span v-for="n in 5" :key="n" class="gd-cd-dot"
                    :class="{ on: n <= tdRes.chan_doan_cap_do.cap_do }"></span>
            </div>
          </div>

          <p v-if="tdRes.chan_doan_cap_do.do_thay_doi_duoc || tdRes.chan_doan_cap_do.phan_loai"
             class="gd-cd-summary">
            <b v-if="tdRes.chan_doan_cap_do.do_thay_doi_duoc">{{ tdRes.chan_doan_cap_do.do_thay_doi_duoc }}</b>
            <span v-if="tdRes.chan_doan_cap_do.do_thay_doi_duoc"> chuyển hoá được</span>
            <span v-if="tdRes.chan_doan_cap_do.do_thay_doi_duoc && tdRes.chan_doan_cap_do.phan_loai"> · </span>
            <span v-if="tdRes.chan_doan_cap_do.phan_loai" class="gd-cd-class">{{ tdRes.chan_doan_cap_do.phan_loai }}</span>
          </p>
          <p v-if="tdRes.chan_doan_cap_do.muc_do_thu_thach" class="gd-mini">{{ tdRes.chan_doan_cap_do.muc_do_thu_thach }}</p>

          <!-- Tín hiệu kích hoạt -->
          <div v-if="(tdRes.chan_doan_cap_do.tin_hieu_kich_hoat || []).length" class="gd-cd-sec">
            <p class="gd-cd-h">🔎 Tín hiệu kích hoạt</p>
            <ul class="gd-cd-signals">
              <li v-for="(t, i) in tdRes.chan_doan_cap_do.tin_hieu_kich_hoat" :key="i">{{ t }}</li>
            </ul>
          </div>

          <!-- LỘ TRÌNH — checklist hành động (mệnh là động từ) -->
          <div v-if="(tdRes.chan_doan_cap_do.lo_trinh || []).length" class="gd-cd-sec">
            <p class="gd-cd-h">🧭 Lộ trình — việc cần LÀM (mệnh là động từ)</p>
            <ul class="gd-cd-steps">
              <li v-for="(s, i) in tdRes.chan_doan_cap_do.lo_trinh" :key="i">
                <span class="gd-cd-check">✓</span><span>{{ s }}</span>
              </li>
            </ul>
          </div>

          <!-- Lộ trình rèn (chi tiết tu/đến/cách) -->
          <div v-if="(tdRes.chan_doan_cap_do.lo_trinh_ren || []).length" class="gd-cd-sec">
            <p class="gd-cd-h">🌿 Đường rèn — chuyển hoá theo chặng</p>
            <div v-for="(r, i) in tdRes.chan_doan_cap_do.lo_trinh_ren" :key="i" class="gd-cd-ren">
              <span class="gd-cd-ren-from">{{ r.tu }}</span>
              <span class="gd-cd-ren-arrow">→</span>
              <span class="gd-cd-ren-to">{{ r.den }}</span>
              <p v-if="r.cach" class="gd-do-text">{{ r.cach }}</p>
            </div>
          </div>

          <p v-if="tdRes.chan_doan_cap_do.ranh_gioi" class="gd-note">⚠ Ranh giới: {{ tdRes.chan_doan_cap_do.ranh_gioi }}</p>
          <p v-if="tdRes.chan_doan_cap_do.doi_chieu_cheo" class="gd-mini">⇄ {{ tdRes.chan_doan_cap_do.doi_chieu_cheo }}</p>

          <p v-if="tdRes.chan_doan_cap_do.nguyen_tac_vang" class="gd-cd-vang">
            “{{ tdRes.chan_doan_cap_do.nguyen_tac_vang }}”
          </p>
          <RefBlock v-if="tdRes.chan_doan_cap_do._nguon" kind="cite">{{ fmtNguon(tdRes.chan_doan_cap_do._nguon) }}</RefBlock>
        </div>

        <!-- KHỐI HỎI–ĐÁP THEO TUỔI -->
        <div v-if="(tdRes.cau_hoi_tuoi || []).length" class="gd-card gd-cht">
          <h5>💬 Hỏi – đáp theo chặng đời</h5>
          <div v-for="(q, i) in tdRes.cau_hoi_tuoi" :key="i" class="gd-cht-item">
            <div class="gd-cht-q">
              <span class="gd-cht-he" :class="'he-' + q.he_tra_loi">{{ heLabel(q.he_tra_loi) }}</span>
              <span class="gd-cht-text">{{ q.cau_hoi }}</span>
            </div>

            <!-- Câu quyết-định → nút Gieo quẻ thay vì trả lời chốt -->
            <div v-if="q.can_gieo_que" class="gd-cht-gieo">
              <p class="gd-note">Đây là câu QUYẾT ĐỊNH — không chốt thay bạn. Gieo một quẻ để soi tâm (không cát/hung).</p>
              <button v-if="gqOpen !== i" class="gd-soft-btn" @click="openGieo(i, q.cau_hoi)">🔮 Gieo quẻ quyết định</button>

              <div v-else class="gd-gieo-box">
                <textarea v-model="gqCauHoi" rows="2" class="gd-in gd-gieo-ta"
                          placeholder="Viết rõ câu hỏi quyết định của bạn (một việc — một quẻ)"></textarea>
                <div class="gd-gieo-actions">
                  <button class="gd-run gd-gieo-run" :disabled="gqLoading || !gqCauHoi.trim()" @click="runGieoQue(i)">
                    {{ gqLoading ? '⏳ Đang gieo...' : '🔮 Gieo quẻ' }}
                  </button>
                  <button class="gd-soft-btn" @click="closeGieo">Đóng</button>
                </div>
                <p v-if="gqErr" class="gd-err">{{ gqErr }}</p>
              </div>

              <!-- Kết quả quẻ -->
              <div v-if="gqRes && gqResFor === i" class="gd-que">
                <p class="gd-que-cauhoi">“{{ gqRes.cau_hoi }}”</p>
                <div class="gd-que-row">
                  <div class="gd-que-cell">
                    <span class="gd-que-tag">Quẻ chính</span>
                    <b>{{ gqRes.que_chinh?.ten_que }}</b>
                    <small v-if="gqRes.que_chinh?.king_wen_index">#{{ gqRes.que_chinh.king_wen_index }}</small>
                  </div>
                  <div class="gd-que-cell">
                    <span class="gd-que-tag">Quẻ hỗ</span>
                    <b>{{ gqRes.que_ho?.ten_que }}</b>
                  </div>
                  <div class="gd-que-cell">
                    <span class="gd-que-tag">Quẻ biến</span>
                    <b>{{ gqRes.que_bien?.ten_que }}</b>
                  </div>
                  <div class="gd-que-cell">
                    <span class="gd-que-tag">Hào động</span>
                    <b>hào {{ gqRes.hao_dong }}</b>
                  </div>
                </div>

                <div v-if="gqRes.the_dung" class="gd-que-td">
                  <p class="gd-mini">
                    <b>Thể:</b> {{ gqRes.the_dung.que_the }} ({{ gqRes.the_dung.ngu_hanh_the }})
                    · <b>Dụng:</b> {{ gqRes.the_dung.que_dung }} ({{ gqRes.the_dung.ngu_hanh_dung }})
                    · <span class="gd-que-quanhe">{{ gqRes.the_dung.quan_he }}</span>
                  </p>
                  <p v-if="gqRes.the_dung.doc_dong_dang" class="gd-do-text">{{ gqRes.the_dung.doc_dong_dang }}</p>
                </div>

                <details class="gd-guide gd-que-buoc">
                  <summary>📿 4 bước đoán quẻ (đọc đồng dạng)</summary>
                  <div v-for="(b, k) in bonBuocList(gqRes.bon_buoc)" :key="k" class="gd-que-buoc-item">
                    <p class="gd-cd-h">{{ b.ten }}</p>
                    <p v-if="b.huong_doc" class="gd-mini">{{ b.huong_doc }}</p>
                    <p v-if="b.cau_hoi_cho_user" class="gd-do-text">❓ {{ b.cau_hoi_cho_user }}</p>
                  </div>
                </details>

                <div v-if="gqRes.tam_phap" class="gd-que-tam">
                  <p v-for="(v, k) in gqRes.tam_phap" :key="k" class="gd-note">• {{ v }}</p>
                </div>
                <p v-if="gqRes._paradigm" class="gd-para">⚖️ {{ gqRes._paradigm }}</p>
              </div>
            </div>

            <!-- Câu thường → trả lời -->
            <div v-else class="gd-cht-a">
              <p>{{ q.tra_loi }}</p>
              <span v-if="q.do_tin != null" class="gd-cht-dotin">độ tin {{ Math.round((q.do_tin <= 1 ? q.do_tin * 100 : q.do_tin)) }}%</span>
            </div>
          </div>
        </div>

        <!-- KHỐI LUẬN CHI TIẾT 12+10 BƯỚC (collapsible) -->
        <details v-if="tdRes.quy_trinh_day_du" class="gd-card gd-qt">
          <summary class="gd-qt-sum">▸ Luận chi tiết 12 + 10 bước</summary>

          <p v-if="tdRes.quy_trinh_day_du.tong_hop_kim_tu_thap" class="gd-qt-tong">
            {{ tdRes.quy_trinh_day_du.tong_hop_kim_tu_thap }}
          </p>

          <!-- Xếp hạng yếu tố -->
          <div v-if="tdRes.quy_trinh_day_du.xep_hang_yeu_to" class="gd-qt-rank">
            <div v-for="grp in xepHangGroups" :key="grp.key"
                 v-show="(tdRes.quy_trinh_day_du.xep_hang_yeu_to[grp.key] || []).length"
                 class="gd-qt-rank-grp" :class="'xh-' + grp.key">
              <p class="gd-cd-h">{{ grp.icon }} {{ grp.label }}</p>
              <ul>
                <li v-for="(y, i) in tdRes.quy_trinh_day_du.xep_hang_yeu_to[grp.key]" :key="i">{{ fmtYeuTo(y) }}</li>
              </ul>
            </div>
          </div>

          <!-- 12 bước Tử Vi -->
          <details v-if="(tdRes.quy_trinh_day_du.tu_vi_12_buoc?.buoc || []).length" class="gd-qt-sub">
            <summary>🏯 Tử Vi — 12 bước</summary>
            <div v-for="(b, i) in tdRes.quy_trinh_day_du.tu_vi_12_buoc.buoc" :key="i" class="gd-qt-step">
              <div class="gd-qt-step-h">
                <span class="gd-qt-no">{{ i + 1 }}</span>
                <b>{{ b.ten_buoc }}</b>
                <small v-if="b.sao_chinh"> · {{ Array.isArray(b.sao_chinh) ? b.sao_chinh.join(', ') : b.sao_chinh }}</small>
                <span v-if="b.muc_do_anh_huong" class="gd-qt-muc">{{ b.muc_do_anh_huong }}</span>
              </div>
              <p v-if="b.luan" class="gd-mini">{{ b.luan }}</p>
            </div>
          </details>

          <!-- 10 bước Bát Tự -->
          <details v-if="(tdRes.quy_trinh_day_du.bat_tu_10_buoc?.buoc || []).length" class="gd-qt-sub">
            <summary>🀄 Bát Tự — 10 bước</summary>
            <div v-for="(b, i) in tdRes.quy_trinh_day_du.bat_tu_10_buoc.buoc" :key="i" class="gd-qt-step">
              <div class="gd-qt-step-h">
                <span class="gd-qt-no">{{ i + 1 }}</span>
                <b>{{ b.ten_buoc }}</b>
                <small v-if="b.sao_chinh"> · {{ Array.isArray(b.sao_chinh) ? b.sao_chinh.join(', ') : b.sao_chinh }}</small>
                <span v-if="b.muc_do_anh_huong" class="gd-qt-muc">{{ b.muc_do_anh_huong }}</span>
              </div>
              <p v-if="b.luan" class="gd-mini">{{ b.luan }}</p>
            </div>
          </details>
        </details>

        <!-- STAGE -->
        <div v-if="tdRes.stage" class="gd-card gd-td-stage">
          <h5>🌱 Chặng đời — tuổi {{ tdRes.stage.tuoi }}</h5>
          <p v-if="tdRes.stage.chua_du_tuoi" class="gd-note">Bạn còn trẻ — đọc như khung tham chiếu, duyên đến tự nhiên.</p>
          <p v-if="tdRes.stage.moi_truong" class="gd-mini"><b>Môi trường:</b> {{ tdRes.stage.moi_truong }}</p>
          <p v-if="tdRes.stage.tam_ly_cot_loi" class="gd-mini"><b>Tâm lý cốt lõi:</b> {{ tdRes.stage.tam_ly_cot_loi }}</p>
          <p v-if="tdRes.stage.cau_hoi_chinh" class="gd-td-quote">“{{ tdRes.stage.cau_hoi_chinh }}”</p>
        </div>

        <!-- PERSONALITY -->
        <div v-if="tdRes.personality" class="gd-card">
          <h5>💗 Khí chất &amp; cách yêu</h5>
          <p v-if="tdRes.personality.menh_chinh_tinh?.length" class="gd-mini">
            Mệnh chính tinh: <b>{{ tdRes.personality.menh_chinh_tinh.join(', ') }}</b>
          </p>
          <p v-else-if="tdRes.personality.vo_chinh_dieu" class="gd-mini">Mệnh vô chính diệu — tính khí mềm, hấp thu theo môi trường.</p>
          <div v-for="(p,i) in (tdRes.personality.profiles||[])" :key="i" class="gd-td-prof">
            <div class="gd-td-prof-h"><b>{{ p.sao }}</b><small v-if="p.ten_han"> · {{ p.ten_han }}</small></div>
            <p v-if="p.khi_chat" class="gd-mini"><b>Khí chất:</b> {{ p.khi_chat }}</p>
            <p v-if="p.cach_yeu" class="gd-mini"><b>Cách yêu:</b> {{ p.cach_yeu }}</p>
            <div v-if="p.khau_vi_giao_tiep" class="gd-td-kv">
              <span v-if="p.khau_vi_giao_tiep.giong" class="gd-td-tag">giọng: {{ p.khau_vi_giao_tiep.giong }}</span>
              <span v-if="p.khau_vi_giao_tiep.nen?.length" class="gd-td-tag ok">nên: {{ p.khau_vi_giao_tiep.nen.join(' · ') }}</span>
              <span v-if="p.khau_vi_giao_tiep.tranh?.length" class="gd-td-tag warn">tránh: {{ p.khau_vi_giao_tiep.tranh.join(' · ') }}</span>
            </div>
            <RefBlock v-if="p._nguon" kind="cite">{{ fmtNguon(p._nguon) }}</RefBlock>
          </div>
        </div>

        <!-- CUNG PHU THÊ (Tử Vi) -->
        <div v-if="tdRes.cung_phu_the_tuvi" class="gd-card">
          <h5>🏯 Cung Phu Thê (Tử Vi) — tại {{ tdRes.cung_phu_the_tuvi.phu_the_branch }}</h5>
          <p v-if="tdRes.cung_phu_the_tuvi.muon_sao_doi_cung" class="gd-note">Vô chính diệu — mượn sao đối cung để luận.</p>
          <p v-if="tdRes.cung_phu_the_tuvi.chinh_tinh?.length" class="gd-mini">
            Chính tinh: <b>{{ tdRes.cung_phu_the_tuvi.chinh_tinh.join(', ') }}</b>
          </p>
          <div v-for="(c,i) in (tdRes.cung_phu_the_tuvi.chinh_tinh_luan||[])" :key="'ct'+i" class="gd-td-line">
            <b>{{ c.sao }}</b><small v-if="c.ten_han"> · {{ c.ten_han }}</small>
            <p v-if="c.tinh_chat_phoi_ngau" class="gd-mini">{{ c.tinh_chat_phoi_ngau }}</p>
            <p v-if="c.dieu_can_chu_y" class="gd-note">⚠ {{ c.dieu_can_chu_y }}</p>
            <RefBlock v-if="c._nguon" kind="cite">{{ fmtNguon(c._nguon) }}</RefBlock>
          </div>
          <div v-for="(d,i) in (tdRes.cung_phu_the_tuvi.dao_hoa_luan||[])" :key="'dh'+i" class="gd-td-line">
            <b>🌸 {{ d.sao }}</b> <span v-if="d.y_nghia_duyen" class="gd-mini">{{ d.y_nghia_duyen }}</span>
            <RefBlock v-if="d._nguon" kind="cite">{{ fmtNguon(d._nguon) }}</RefBlock>
          </div>
          <div v-for="(s,i) in (tdRes.cung_phu_the_tuvi.sat_tinh_luan||[])" :key="'st'+i" class="gd-td-line">
            <b class="gd-td-warn">{{ s.sao }}</b> <span v-if="s.y_nghia" class="gd-mini">{{ s.y_nghia }}</span>
            <RefBlock v-if="s._nguon" kind="cite">{{ fmtNguon(s._nguon) }}</RefBlock>
          </div>
          <div v-for="(h,i) in (tdRes.cung_phu_the_tuvi.tu_hoa_luan||[])" :key="'th'+i" class="gd-td-line">
            <b>Hóa {{ h.hoa }}</b> ({{ h.sao }}) <span v-if="h.y_nghia" class="gd-mini">{{ h.y_nghia }}</span>
            <RefBlock v-if="h._nguon" kind="cite">{{ fmtNguon(h._nguon) }}</RefBlock>
          </div>
        </div>

        <!-- BÁT TỰ HÔN NHÂN -->
        <div v-if="tdRes.batu_hon_nhan" class="gd-card">
          <h5>🀄 Hôn nhân theo Bát Tự</h5>
          <p class="gd-mini">Nhật chủ <b>{{ tdRes.batu_hon_nhan.nhat_chu }}</b> · Nhật chi <b>{{ tdRes.batu_hon_nhan.nhat_chi }}</b>
            <span v-if="tdRes.batu_hon_nhan.nhat_chi_la_dao_hoa"> · 🌸 đào hoa</span></p>
          <p v-if="tdRes.batu_hon_nhan.trang_thai_luan" class="gd-mini">
            <b>Sao chồng (官杀):</b> {{ tdRes.batu_hon_nhan.trang_thai_luan.mo_ta || tdRes.batu_hon_nhan.trang_thai_luan }}
          </p>
          <p v-if="tdRes.batu_hon_nhan.trang_thai_luan?.van_hanh" class="gd-do-text">→ {{ tdRes.batu_hon_nhan.trang_thai_luan.van_hanh }}</p>
          <p v-if="tdRes.batu_hon_nhan.phoi_ngau_cung_luan" class="gd-mini">
            <b>Cung phối ngẫu (日支):</b> {{ tdRes.batu_hon_nhan.phoi_ngau_cung_luan.mo_ta || tdRes.batu_hon_nhan.phoi_ngau_cung_luan }}
          </p>
          <RefBlock v-if="tdRes.batu_hon_nhan._nguon" kind="cite">{{ fmtNguon(tdRes.batu_hon_nhan._nguon) }}</RefBlock>
        </div>

        <!-- SONG PHÁI RECONCILE -->
        <div v-if="(tdRes.song_phai_reconcile||[]).length" class="gd-card gd-td-recon">
          <h5>⇄ Song phái — Tử Vi ⇄ Bát Tự (hội tụ / dị biệt)</h5>
          <div v-for="(r,i) in tdRes.song_phai_reconcile" :key="i" class="gd-td-recon-row">
            <div class="gd-td-recon-h">{{ r.chu_de }}</div>
            <p v-if="r.tuvi_doc_bang" class="gd-mini"><span class="gd-td-pill tv">Tử Vi</span> {{ r.tuvi_doc_bang }}</p>
            <p v-if="r.batu_doc_bang" class="gd-mini"><span class="gd-td-pill bt">Bát Tự</span> {{ r.batu_doc_bang }}</p>
            <p v-if="r.khi_HOI_TU" class="gd-do-text">✓ Hội tụ: {{ r.khi_HOI_TU }}</p>
            <p v-if="r.khi_DI_BIET" class="gd-note">⚖ Dị biệt: {{ r.khi_DI_BIET }}</p>
            <p v-if="r.phai_uu_tien" class="gd-mini">Ưu tiên đọc: <b>{{ r.phai_uu_tien }}</b></p>
            <RefBlock v-if="r._nguon" kind="cite">{{ fmtNguon(r._nguon) }}</RefBlock>
          </div>
        </div>

        <!-- CÁCH CỤC (bien_chinh — đọc đồng dạng) -->
        <div v-if="(tdRes.cach_cuc||[]).length" class="gd-card">
          <h5>📐 Cách cục — đọc đồng dạng (không phán bản án)</h5>
          <div v-for="(c,i) in tdRes.cach_cuc" :key="i" class="gd-td-cach"
               :class="'cc-' + (c.cat_hung || 'trung_tinh')">
            <div class="gd-td-cach-h">
              <b>{{ c.ten_cach }}</b>
              <span class="gd-td-cach-tag" :class="'cc-' + (c.cat_hung || 'trung_tinh')">
                {{ catHungLabel(c.cat_hung) }}
              </span>
              <span v-if="c.uu_tien_phu_the" class="gd-td-cach-pt">cung Phu Thê</span>
            </div>
            <p class="gd-mini">{{ c.bien_chinh }}</p>
            <p v-if="c.van_hanh && c.van_hanh !== c.bien_chinh" class="gd-do-text">→ {{ c.van_hanh }}</p>
            <RefBlock v-if="c._nguon" kind="cite">{{ fmtNguon(c._nguon) }}</RefBlock>
          </div>
        </div>

        <!-- ĐỊNH THỜI -->
        <div v-if="tdRes.dinh_thoi" class="gd-card gd-td-thoi">
          <h5>📅 Định thời — năm khí được kích hoạt / cần giữ gìn</h5>
          <div v-if="(tdRes.dinh_thoi.nam_kich_hoat||[]).length">
            <p class="gd-mini"><b>Đại vận có khí hỉ sự / duyên kích hoạt:</b></p>
            <div class="gd-years">
              <span v-for="(n,i) in tdRes.dinh_thoi.nam_kich_hoat" :key="'k'+i" class="gd-year">
                <b>{{ n.start_age }}–{{ n.end_age }} tuổi</b>
                <small>({{ (n.sao_kich_hoat||[]).join('/') }})</small>
              </span>
            </div>
          </div>
          <div v-if="(tdRes.dinh_thoi.nam_can_giu_gin||[]).length">
            <p class="gd-mini"><b>Đại vận cần GIỮ GÌN / chăm sóc quan hệ:</b></p>
            <div class="gd-years">
              <span v-for="(n,i) in tdRes.dinh_thoi.nam_can_giu_gin" :key="'g'+i" class="gd-year dam">
                <b>{{ n.start_age }}–{{ n.end_age }} tuổi</b>
                <small>({{ (n.ly_do||[]).join('; ') }})</small>
              </span>
            </div>
          </div>
          <p v-if="!(tdRes.dinh_thoi.nam_kich_hoat||[]).length && !(tdRes.dinh_thoi.nam_can_giu_gin||[]).length" class="gd-note">
            Không có mốc đại vận nổi bật trong tầm tuổi — duyên vận hành đều, chủ động vẫn hơn.
          </p>
          <p v-if="tdRes.dinh_thoi.bien_chinh_hien_dai" class="gd-note">{{ tdRes.dinh_thoi.bien_chinh_hien_dai }}</p>
        </div>

        <!-- LỜI THẦY (narrate) -->
        <div class="gd-card gd-tho-card">
          <button v-if="!tdNarr && !tdNarrLoading" class="gd-soft-btn" @click="runTinhDuyenNarrate">✍️ Nghe lời thầy luận tình duyên</button>
          <p v-if="tdNarrLoading" class="gd-mini">✍️ Thầy đang viết...</p>
          <div v-if="tdNarr" class="gd-tho">
            <div class="gd-td-narr-h">✍️ Lời thầy</div>
            {{ tdNarr }}
          </div>
        </div>

        <!-- NGUỒN -->
        <details v-if="(tdRes.sources||[]).length" class="gd-guide">
          <summary>📚 Nguồn tri thức</summary>
          <ul><li v-for="(s,i) in tdRes.sources" :key="i">{{ s }}</li></ul>
        </details>

        <p v-if="tdRes._disclaimer" class="gd-para">⚖️ {{ tdRes._disclaimer }}</p>
      </div>
    </section>

    <!-- CHẾ ĐỘ ĐÃ CÓ ĐÔI: Xem tuổi đôi lứa -->
    <section v-if="mode === 'cap'" class="gd-tool">
      <h3>🔮 Xem tuổi đôi lứa — ba hệ</h3>
      <p class="gd-tool-sub">Nhập lá số của bạn và một lá số khác. Hệ thống soi Tử Vi · Bát Tự · Kinh Dịch, chấm độ <em>tương ứng</em> và gợi ý <strong>gia quy</strong>.</p>
      <div class="gd-form">
        <div class="gd-person">
          <h4>Người 1 (bạn)</h4>
          <input v-model="n1" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="b1" type="datetime-local" class="gd-in" />
          <select v-model="g1" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
        <div class="gd-heart">💞</div>
        <div class="gd-person">
          <h4>Người 2</h4>
          <input v-model="n2" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="b2" type="datetime-local" class="gd-in" />
          <select v-model="g2" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
      </div>
      <button class="gd-run" :disabled="!b1 || !b2 || loading" @click="run">
        {{ loading ? '⏳ Đang soi ba hệ...' : '✨ Xem tương ứng' }}
      </button>
      <p v-if="err" class="gd-err">{{ err }}</p>

      <!-- Kết quả -->
      <div v-if="res" class="gd-result">
        <div class="gd-score">
          <div class="gd-score-num">{{ res.diem_tong }}<span>/100</span></div>
          <div class="gd-score-muc">{{ res.muc }}</div>
        </div>

        <div class="gd-truc" :class="res.truc_cuong_nhu.ung_nhau ? 'ung' : 'chua'">
          <strong>Trục Cương–Nhu:</strong>
          {{ res.ten1 }} <b>{{ res.truc_cuong_nhu.xu_huong_1 }}</b> ·
          {{ res.ten2 }} <b>{{ res.truc_cuong_nhu.xu_huong_2 }}</b>
          {{ res.truc_cuong_nhu.ung_nhau ? '→ ỨNG NHAU ✓' : '' }}
          <div class="gd-truc-gt">{{ res.truc_cuong_nhu.giai_thich }}</div>
        </div>

        <div class="gd-he">
          <span>Tử Vi <b>{{ res.tu_vi.diem }}</b></span>
          <span>Bát Tự <b>{{ res.bat_tu.diem }}</b></span>
          <span>Kinh Dịch <b>{{ res.ha_lac.diem }}</b></span>
        </div>

        <div class="gd-cols">
          <div class="gd-col khoa">
            <h5>🔑 Khóa duyên</h5>
            <ul><li v-for="(k,i) in res.khoa_duyen" :key="i">{{ k }}</li></ul>
          </div>
          <div class="gd-col giu">
            <h5>🛠 Chỗ phải giữ</h5>
            <ul><li v-for="(c,i) in res.cho_phai_giu" :key="i">{{ c }}</li></ul>
          </div>
        </div>

        <div class="gd-giaquy">
          <h5>📜 Gia quy gợi ý cho hai bạn</h5>
          <ol><li v-for="(g,i) in res.gia_quy" :key="i">{{ g }}</li></ol>
        </div>

        <div v-if="res.nghe_nghiep" class="gd-card">
          <h5>💼 Nghề nghiệp đôi bên</h5>
          <p class="gd-mini"><b>{{ res.ten1 }}</b> ({{ res.nghe_nghiep.nguoi1.thien_huong }}): {{ (res.nghe_nghiep.nguoi1.nghe || []).join('; ') }}</p>
          <p class="gd-mini"><b>{{ res.ten2 }}</b> ({{ res.nghe_nghiep.nguoi2.thien_huong }}): {{ (res.nghe_nghiep.nguoi2.nghe || []).join('; ') }}</p>
          <p class="gd-note">{{ res.nghe_nghiep.doi_ben }}</p>
        </div>
        <div v-if="res.con_cai" class="gd-card" :class="{ 'gd-hit': res.con_cai.khop }">
          <h5>👶 Con cái có khớp không</h5>
          <p class="gd-mini">Cung Con Cái: {{ res.ten1 }} ở {{ res.con_cai.chi_nguoi1 }} · {{ res.ten2 }} ở {{ res.con_cai.chi_nguoi2 }}
            <b v-if="res.con_cai.quan_he"> ({{ res.con_cai.quan_he }})</b></p>
          <p class="gd-note">{{ res.con_cai.ghi_chu }}</p>
        </div>

        <div v-if="res.nam_hop_cuoi && res.nam_hop_cuoi.nam.length" class="gd-card">
          <h5>📅 Năm hợp cưới ({{ res.nam_hop_cuoi.tu_nam }}–{{ res.nam_hop_cuoi.den_nam }})</h5>
          <div class="gd-years">
            <span v-for="(y,i) in res.nam_hop_cuoi.nam" :key="i" class="gd-year" :class="{ dam: y.ca_hai }">
              <b>{{ y.nam }}</b> <small>{{ y.ca_hai ? '⭐ cả hai' : 'một người' }}</small>
            </span>
          </div>
          <p class="gd-note">{{ res.nam_hop_cuoi.ghi_chu }}</p>
        </div>

        <div class="gd-share">
          <button class="gd-soft-btn" @click="shareCard(res.ten1+' 💞 '+res.ten2, res.muc, 'Trục cương–nhu: '+(res.truc_cuong_nhu.ung_nhau?'ứng nhau ✓':'cần dung hòa'), res.diem_tong)">📤 Tạo thẻ chia sẻ</button>
        </div>

        <details class="gd-guide">
          <summary>📖 Hướng dẫn đọc kết quả (đọc trước khi tin)</summary>
          <ul><li v-for="(h,i) in res.huong_dan" :key="i">{{ h }}</li></ul>
          <p class="gd-para">⚖️ {{ res.paradigm }}</p>
        </details>
      </div>

      <!-- #55 — Hôn nhân – Gia đình (song phái): Bát Tự THỂ × Tử Vi DỤNG, 12 khía cạnh.
           Khung dựng sẵn (Anh duyệt 2026-06-19) — nối vào luận sâu (30 xu) của chính bạn. -->
      <details class="gd-songphai">
        <summary>🀄 Hôn nhân – Gia đình (song phái) · 12 khía cạnh — luận sâu</summary>
        <p class="gd-tool-sub">
          Hợp nhất <b>Bát Tự (THỂ — bạn là ai)</b> và <b>Tử Vi (DỤNG — bạn vận hành điều gì)</b>
          trên <b>lá số của chính bạn</b>. Hai phái cùng hướng → <em>đồng-tham</em> (tin cao);
          lệch hướng → <em>dị-tham</em> (giữ cả hai, thận trọng). Mệnh là động từ — không bói cát/hung.
        </p>
        <div class="gd-sp-grid">
          <div v-for="a in songPhaiAspects" :key="a.id" class="gd-sp-cell"
               :class="spResult ? ('c-' + (spById[a.id]?.concord || 'mot')) : ''">
            <div class="gd-sp-head">
              <span class="gd-sp-id">{{ a.id }}</span>
              <span class="gd-sp-ten">{{ a.ten }}</span>
              <span class="gd-sp-lead" :class="a.lead">{{ a.lead === 'bat_tu' ? 'Bát Tự' : 'Tử Vi' }}</span>
            </div>
            <div v-if="spResult && spById[a.id]" class="gd-sp-body">
              <span class="gd-sp-concord">{{ concordLabel(spById[a.id].concord) }}</span>
              <p class="gd-sp-read">{{ spById[a.id].lead_reading }}</p>
              <p v-if="spById[a.id].cross_reading" class="gd-sp-cross">↔ {{ spById[a.id].cross_reading }}</p>
              <small v-if="spById[a.id].unsourced" class="gd-sp-uns">chưa có nguồn corpus</small>
            </div>
            <div v-else class="gd-sp-body gd-sp-skel">
              <span class="gd-sp-concord">—</span>
              <p class="gd-sp-read">Mở luận để soi khía cạnh này.</p>
            </div>
          </div>
        </div>
        <button class="gd-run gd-sp-open" :disabled="spLoading" @click="openSongPhai">
          {{ spLoading ? '⏳ Đang luận...' : '🔓 Mở luận sâu (30 xu)' }}
        </button>
        <p v-if="spErr" class="gd-err">{{ spErr }}</p>
        <p v-if="spResult && spResult.cached" class="gd-note">♻️ Lượt hỏi gần đây — không trừ xu lại (một việc một lần).</p>
        <p v-if="spResult" class="gd-para">⚖️ {{ spResult.paradigm }}</p>
      </details>
    </section>

    <details class="gd-book-toggle">
      <summary>📖 Đọc sách <b>"Gieo Duyên"</b> — đúc kết đầy đủ qua 3 hệ (một ca điển hình)</summary>
      <article class="gd-body reading-surface" v-html="rendered"></article>
      <p class="gd-foot">Cuốn sách là đúc kết của một ca điển hình. Công cụ phía trên áp cùng phương pháp cho lá số bất kỳ — đọc đồng dạng, không bói toán.</p>
    </details>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import manuscript from "../content/gieo-duyen.md?raw";
import { activeBirthDatetime, activePerson } from "../stores/userDataStore.js";
import RefBlock from "./RefBlock.vue";
import { sessionToken } from "../stores/authStore.js";
import { tuviPersonName, tuviPersonBirth, tuviPersonGender } from "../stores/tuviPersonStore.js";

const mode = ref("tim");  // 'tim' | 'cap' | 'so' | 'tinh'

// Auth headers (cookie session + token), giống tuviPersonStore.
function _authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

// ── Chế độ TÌNH DUYÊN (nữ mệnh) — đọc trên lá số của chính bạn ──
const tdLoading = ref(false); const tdRes = ref(null); const tdErr = ref("");
const tdNarr = ref(""); const tdNarrLoading = ref(false);
const tdWho = computed(() => tuviPersonName?.value || "");
const tdBirth = computed(() => (tuviPersonBirth?.value || "").slice(0, 16).replace("T", " "));
const tdGender = computed(() => {
  const g = tuviPersonGender?.value;
  return g === "nữ" || g === "nu" || g === "F" ? "nữ" : g === "nam" || g === "M" ? "nam" : "";
});

function fmtNguon(n) {
  if (!n) return "";
  if (typeof n === "string") return n;
  if (Array.isArray(n)) return n.map(fmtNguon).filter(Boolean).join("; ");
  if (typeof n === "object") {
    return [n.sach, n.title, n.quyen, n.trang, n.chuong, n.ghi_chu]
      .filter(Boolean).join(" · ") || JSON.stringify(n);
  }
  return String(n);
}

function catHungLabel(c) {
  return c === "the_manh" ? "✓ thế mạnh" : c === "diem_can_chu_y" ? "⚠ cần chú ý" : "• trung tính";
}

async function runTinhDuyen() {
  tdLoading.value = true; tdErr.value = ""; tdRes.value = null; tdNarr.value = "";
  try {
    const r = await fetch("/api/cross-paradigm/tinh-duyen", {
      method: "POST",
      headers: _authHeaders(),
      credentials: "include",
      body: JSON.stringify({ person_key: "self" }),
    });
    let d = null;
    try { d = await r.json(); } catch (_) { d = null; }
    if (r.status === 401) { tdErr.value = "Đăng nhập để xem tình duyên trên lá số của bạn."; return; }
    if (r.status === 402) {
      const need = (d && (d.detail?.need_xu ?? d.need_xu ?? d.required_xu)) || 30;
      const have = d && (d.detail?.xu_balance ?? d.xu_balance);
      tdErr.value = `Không đủ xu — cần ${need} xu để xem tình duyên` +
        (have != null ? ` (bạn đang có ${have} xu).` : ".") + " Nạp thêm để mở luận.";
      return;
    }
    if (r.status === 422) { tdErr.value = "Cần cập nhật giờ sinh của bạn trước khi xem."; return; }
    if (!r.ok) { tdErr.value = (d && (d.detail || d.error)) || "Không xem được, thử lại."; return; }
    tdRes.value = d;
  } catch (e) {
    tdErr.value = "Lỗi kết nối, thử lại.";
  } finally {
    tdLoading.value = false;
  }
}

async function runTinhDuyenNarrate() {
  // Narrate optional — lỗi KHÔNG làm vỡ UI.
  tdNarrLoading.value = true; tdNarr.value = "";
  try {
    const r = await fetch("/api/cross-paradigm/tinh-duyen/narrate", {
      method: "POST",
      headers: _authHeaders(),
      credentials: "include",
      body: JSON.stringify({ person_key: "self" }),
    });
    const d = await r.json().catch(() => null);
    if (r.ok && d && d.narration) tdNarr.value = d.narration;
    else tdNarr.value = "";
  } catch (e) {
    tdNarr.value = "";
  } finally {
    tdNarrLoading.value = false;
  }
}

// ── Hỏi–đáp theo tuổi: badge hệ + gieo quẻ quyết định ──
function heLabel(he) {
  return he === "bat_tu" ? "Bát Tự" : he === "mai_hoa" ? "Mai Hoa" : "Tử Vi";
}

const gqOpen = ref(-1);        // index câu đang mở ô gieo quẻ
const gqCauHoi = ref("");
const gqLoading = ref(false);
const gqErr = ref("");
const gqRes = ref(null);
const gqResFor = ref(-1);      // index câu mà kết quả quẻ thuộc về

function openGieo(i, prefill) {
  gqOpen.value = i;
  gqErr.value = "";
  if (gqResFor.value !== i) { gqRes.value = null; gqResFor.value = -1; }
  if (!gqCauHoi.value.trim()) gqCauHoi.value = prefill || "";
}
function closeGieo() { gqOpen.value = -1; gqErr.value = ""; }

async function runGieoQue(i) {
  const cauHoi = gqCauHoi.value.trim();
  if (!cauHoi) { gqErr.value = "Viết câu hỏi quyết định trước khi gieo (không nghi không bói)."; return; }
  gqLoading.value = true; gqErr.value = "";
  try {
    const r = await fetch("/api/cross-paradigm/tinh-duyen/gieo-que", {
      method: "POST",
      headers: _authHeaders(),
      credentials: "include",
      body: JSON.stringify({ cau_hoi: cauHoi }),
    });
    const d = await r.json().catch(() => null);
    if (r.status === 401) { gqErr.value = "Đăng nhập để gieo quẻ."; return; }
    if (r.status === 422) { gqErr.value = (d && (d.detail || d.error)) || "Thiếu câu hỏi — một câu một quẻ."; return; }
    if (!r.ok) { gqErr.value = (d && (d.detail || d.error)) || "Không gieo được, thử lại."; return; }
    gqRes.value = d;
    gqResFor.value = i;
    gqOpen.value = -1;  // thu ô nhập, hiện kết quả (một việc một lần)
  } catch (e) {
    gqErr.value = "Lỗi kết nối, thử lại.";
  } finally {
    gqLoading.value = false;
  }
}

// 4 bước đoán quẻ -> mảng theo thứ tự để render
function bonBuocList(bb) {
  if (!bb) return [];
  const order = ["buoc_1_loi_que_hao", "buoc_2_the_dung", "buoc_3_ngoai_ung", "buoc_4_tu_the"];
  const out = [];
  for (const k of order) {
    const b = bb[k];
    if (!b) continue;
    out.push({
      ten: b.ten,
      huong_doc: b.huong_doc,
      cau_hoi_cho_user: b.cau_hoi_cho_user,
    });
  }
  return out;
}

// ── Luận chi tiết: nhóm xếp hạng yếu tố ──
const xepHangGroups = [
  { key: "truc_tiep", label: "Trực tiếp", icon: "🎯" },
  { key: "gian_tiep", label: "Gián tiếp", icon: "🔗" },
  { key: "tiem_an", label: "Tiềm ẩn", icon: "🌫" },
];
function fmtYeuTo(y) {
  if (y == null) return "";
  if (typeof y === "string") return y;
  if (typeof y === "object") {
    return [y.ten || y.yeu_to || y.ten_buoc, y.luan || y.mo_ta || y.ghi_chu]
      .filter(Boolean).join(" — ") || JSON.stringify(y);
  }
  return String(y);
}

// Món 2: lời văn ấm
const dtho = ref(""); const dthoLoading = ref(false);
async function runDuyenTho() {
  if (!db.value) return;
  dthoLoading.value = true; dtho.value = "";
  try {
    const r = await fetch("/api/tu-vi/duyen-tho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth: db.value, gender: dg.value }),
    });
    const d = await r.json();
    dtho.value = d.narrative || ("Lỗi: " + (d.error || "thử lại"));
  } catch (e) { dtho.value = "Lỗi kết nối."; } finally { dthoLoading.value = false; }
}

// Món 1: so nhiều người
const soMe = ref({ ten: "", birth: "", gender: "nam" });
const soOthers = ref([{ ten: "", birth: "", gender: "nữ" }, { ten: "", birth: "", gender: "nữ" }]);
const soRes = ref(null); const soLoading = ref(false); const soErr = ref("");
function addOther() { if (soOthers.value.length < 8) soOthers.value.push({ ten: "", birth: "", gender: "nữ" }); }
function rmOther(i) { soOthers.value.splice(i, 1); }
async function runSoSanh() {
  if (!soMe.value.birth) { soErr.value = "Nhập lá số của bạn."; return; }
  const others = soOthers.value.filter(o => o.birth);
  if (!others.length) { soErr.value = "Nhập ít nhất 1 người để so."; return; }
  soLoading.value = true; soErr.value = ""; soRes.value = null;
  try {
    const r = await fetch("/api/tu-vi/so-sanh-duyen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ me: soMe.value, others }),
    });
    const d = await r.json();
    if (d.error) soErr.value = d.error; else soRes.value = d;
  } catch (e) { soErr.value = "Lỗi kết nối."; } finally { soLoading.value = false; }
}

// Món 4: thẻ chia sẻ (SVG → tải ảnh)
function shareCard(title, line1, line2, score) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="315" viewBox="0 0 600 315">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff6f0"/><stop offset="1" stop-color="#fbe6ef"/></linearGradient></defs>
    <rect width="600" height="315" fill="url(#g)"/>
    <rect x="12" y="12" width="576" height="291" rx="18" fill="none" stroke="#d9a7b8" stroke-width="2"/>
    <text x="300" y="70" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="#9c3a5a">💞 Gieo Duyên</text>
    <text x="300" y="108" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#7d4357">${_esc(title)}</text>
    ${score != null ? `<text x="300" y="185" text-anchor="middle" font-family="Georgia,serif" font-size="64" font-weight="bold" fill="#9c3a5a">${score}<tspan font-size="22" fill="#c98aa0">/100</tspan></text>` : ""}
    <text x="300" y="${score != null ? 230 : 175}" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#5d4450">${_esc(line1)}</text>
    <text x="300" y="${score != null ? 256 : 205}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#8a7079">${_esc(line2)}</text>
    <text x="300" y="292" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b89aa3">kinhdich.online · đọc đồng dạng, không bói toán</text>
  </svg>`;
  const img = new Image();
  const blob = new Blob([svg], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);
  img.onload = () => {
    const c = document.createElement("canvas"); c.width = 1200; c.height = 630;
    const ctx = c.getContext("2d"); ctx.scale(2, 2); ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);
    c.toBlob((b) => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(b); a.download = "gieo-duyen.png"; a.click();
    });
  };
  img.src = url;
}
function _esc(s) { return String(s || "").slice(0, 80).replace(/[<>&]/g, ""); }

// ── Chế độ ĐANG TÌM: Duyên của tôi ──
const dn = ref(""); const db = ref(""); const dg = ref("nam");
const dloading = ref(false); const dres = ref(null); const derr = ref("");
async function runDuyen() {
  if (!db.value) return;
  dloading.value = true; derr.value = ""; dres.value = null;
  try {
    const r = await fetch("/api/tu-vi/duyen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth: db.value, gender: dg.value }),
    });
    const d = await r.json();
    if (d.error) derr.value = d.error; else dres.value = d;
  } catch (e) { derr.value = "Lỗi kết nối, thử lại."; } finally { dloading.value = false; }
}

// ── Công cụ Xem tuổi đôi lứa ──
const n1 = ref(""); const b1 = ref(""); const g1 = ref("nam");
const n2 = ref(""); const b2 = ref(""); const g2 = ref("nữ");
const loading = ref(false); const res = ref(null); const err = ref("");

onMounted(() => {
  // prefill lá số người dùng nếu đã đăng nhập / có active person
  const bd = activeBirthDatetime?.value;
  if (bd) { b1.value = String(bd).slice(0, 16); db.value = String(bd).slice(0, 16); }
  const p = activePerson?.value;
  if (p?.name) { n1.value = p.name; dn.value = p.name; }
  if (p?.gender) {
    const gg = p.gender === "nữ" || p.gender === "nu" || p.gender === "F" ? "nữ" : "nam";
    g1.value = gg; dg.value = gg;
  }
});

async function run() {
  if (!b1.value || !b2.value) return;
  loading.value = true; err.value = ""; res.value = null;
  try {
    const r = await fetch("/api/tu-vi/hop-hon", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth1: b1.value, gender1: g1.value, ten1: n1.value || "Người 1",
        birth2: b2.value, gender2: g2.value, ten2: n2.value || "Người 2",
      }),
    });
    const d = await r.json();
    if (d.error) { err.value = d.error; } else { res.value = d; }
  } catch (e) { err.value = "Lỗi kết nối, thử lại."; } finally { loading.value = false; }
}

// #55 — Hôn nhân song phái (12 khía cạnh). Ma trận đồng bộ engine
// engine/cross_paradigm/hon_nhan_song_phai.ASPECTS — KHUNG dựng sẵn, cắm dữ liệu khi mở luận.
const songPhaiAspects = [
  { id: 1, ten: "Tính cách / khí chất phối ngẫu", lead: "tu_vi" },
  { id: 2, ten: "Chất lượng hôn nhân tổng thể", lead: "tu_vi" },
  { id: 3, ten: "Ứng kỳ (khoảng kích hoạt quan hệ)", lead: "tu_vi" },
  { id: 4, ten: "Năng lượng tương tác hợp / khắc", lead: "bat_tu" },
  { id: 5, ten: "'Cao thấp' / lực của Thê tinh", lead: "bat_tu" },
  { id: 6, ten: "Hợp đôi (hai người)", lead: "bat_tu" },
  { id: 7, ten: "Điểm căng quan hệ (xa cách / biến động)", lead: "tu_vi" },
  { id: 8, ten: "Con cái — cách nuôi dưỡng / truyền tính", lead: "tu_vi" },
  { id: 9, ten: "Cha mẹ / anh chị em", lead: "bat_tu" },
  { id: 10, ten: "Tâm lý / EQ hôn nhân (khí số)", lead: "tu_vi" },
  { id: 11, ten: "Tài sản chung / kinh tế gia đình", lead: "bat_tu" },
  { id: 12, ten: "Định khắc giờ sinh (định bàn)", lead: "tu_vi" },
];
const spLoading = ref(false); const spResult = ref(null); const spErr = ref("");
const spById = computed(() => {
  const m = {};
  for (const k of (spResult.value?.khia_canh || [])) m[k.id] = k;
  return m;
});
function concordLabel(c) {
  return c === "đồng_tham" ? "✓ đồng-tham" : c === "dị_tham" ? "⚠ dị-tham" : "• một-phía";
}
async function openSongPhai() {
  spLoading.value = true; spErr.value = "";
  try {
    const r = await fetch("/api/cross-paradigm/hon-nhan", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_key: "self" }),
    });
    if (r.status === 401) { spErr.value = "Đăng nhập để mở luận sâu trên lá số của bạn."; return; }
    if (r.status === 402) { spErr.value = "Không đủ xu (cần 30 xu) — nạp thêm để mở luận."; return; }
    if (r.status === 422) { spErr.value = "Cần cập nhật giờ sinh của bạn trước khi luận."; return; }
    const d = await r.json();
    if (!r.ok) { spErr.value = (d && d.detail) || "Không mở được luận, thử lại."; return; }
    spResult.value = d;
  } catch (e) { spErr.value = "Lỗi kết nối, thử lại."; } finally { spLoading.value = false; }
}

// Markdown nhẹ → HTML (đủ cho sách: heading, đậm, nghiêng, trích dẫn, bảng, hr, list)
function renderMarkdown(md) {
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const lines = md.split("\n");
  const out = [];
  let i = 0;
  const inline = (t) =>
    esc(t)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`(.+?)`/g, "<code>$1</code>");
  while (i < lines.length) {
    let ln = lines[i];
    if (/^\s*$/.test(ln)) { i++; continue; }
    // bảng
    if (ln.includes("|") && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
      const header = ln.split("|").map((c) => c.trim()).filter(Boolean);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].includes("|")) {
        rows.push(lines[i].split("|").map((c) => c.trim()).filter((_, k, a) => !(k === 0 && a[0] === "") ));
        i++;
      }
      let t = "<table><thead><tr>" + header.map((h) => `<th>${inline(h)}</th>`).join("") + "</tr></thead><tbody>";
      for (const r of rows) {
        const cells = r.filter((c) => c !== "");
        t += "<tr>" + cells.map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>";
      }
      t += "</tbody></table>";
      out.push(t);
      continue;
    }
    if (/^####\s/.test(ln)) { out.push(`<h5>${inline(ln.replace(/^####\s/, ""))}</h5>`); i++; continue; }
    if (/^###\s/.test(ln)) { out.push(`<h4>${inline(ln.replace(/^###\s/, ""))}</h4>`); i++; continue; }
    if (/^##\s/.test(ln)) { out.push(`<h3>${inline(ln.replace(/^##\s/, ""))}</h3>`); i++; continue; }
    if (/^#\s/.test(ln)) { out.push(`<h2 class="gd-h1">${inline(ln.replace(/^#\s/, ""))}</h2>`); i++; continue; }
    if (/^>\s?/.test(ln)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(inline(lines[i].replace(/^>\s?/, ""))); i++; }
      out.push(`<blockquote>${buf.join("<br>")}</blockquote>`);
      continue;
    }
    if (/^(-{3,}|\*{3,})\s*$/.test(ln)) { out.push("<hr>"); i++; continue; }
    if (/^\s*[-*]\s+/.test(ln) || /^\s*\d+\.\s+/.test(ln)) {
      const ordered = /^\s*\d+\.\s+/.test(ln);
      const buf = [];
      while (i < lines.length && (/^\s*[-*]\s+/.test(lines[i]) || /^\s*\d+\.\s+/.test(lines[i]))) {
        buf.push(`<li>${inline(lines[i].replace(/^\s*(?:[-*]|\d+\.)\s+/, ""))}</li>`);
        i++;
      }
      out.push((ordered ? "<ol>" : "<ul>") + buf.join("") + (ordered ? "</ol>" : "</ul>"));
      continue;
    }
    // đoạn văn
    const buf = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^[#>|]/.test(lines[i]) && !/^(-{3,})/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i])) {
      buf.push(inline(lines[i]));
      i++;
    }
    out.push(`<p>${buf.join(" ")}</p>`);
  }
  return out.join("\n");
}

const rendered = computed(() => renderMarkdown(manuscript));
</script>

<style scoped>
.gieo-duyen { max-width: 760px; margin: 0 auto; padding: 16px; }
.gd-hero { text-align: center; padding: 28px 16px 22px; background: linear-gradient(160deg,#fff6f0,#fdeef5); border: 1px solid #e8cdd6; border-radius: 16px; margin-bottom: 22px; }
.gd-hero-icon { font-size: 2.4em; }
.gd-hero h2 { margin: 6px 0 4px; font-size: 1.9em; color: #9c3a5a; letter-spacing: 1px; }
.gd-sub { margin: 4px 0; color: #6a4555; font-size: 0.98em; }
.gd-tag { margin: 8px 0 0; color: #9a7886; font-size: 0.84em; font-style: italic; }
.gd-actions { margin-top: 16px; }
.gd-pdf-btn { display: inline-block; padding: 10px 22px; border-radius: 24px; background: #9c3a5a; color: #fff; text-decoration: none; font-size: 0.92em; transition: all .15s; }
.gd-pdf-btn:hover { background: #7d2c47; transform: translateY(-1px); }

/* Chọn chế độ */
.gd-mode { display: flex; gap: 10px; justify-content: center; margin-bottom: 18px; }
.gd-mode button { flex: 1; max-width: 260px; padding: 12px; border: 1.5px solid #d8b8c3; border-radius: 24px; background: transparent; color: #9c3a5a; font: inherit; font-size: 0.95em; cursor: pointer; transition: all .15s; }
.gd-mode button.on { background: #9c3a5a; color: #fff; border-color: #9c3a5a; }
.gd-mode button:hover:not(.on) { background: #fbeef2; }

/* Thẻ kết quả duyên */
.gd-card { margin: 12px 0; padding: 14px 16px; background: #fdf6f8; border: 1px solid #ecd7df; border-radius: 12px; }
.gd-card h5 { margin: 0 0 8px; color: #9c3a5a; font-size: 1em; }
.gd-card h5 b { text-transform: capitalize; }
.gd-card ul { margin: 6px 0; padding-left: 18px; } .gd-card li { margin: 5px 0; font-size: 0.9em; line-height: 1.55; color: var(--read-text,#3a3a38); }
.gd-card ul.gd-do li { color: #2e7d32; }
.gd-mini { margin: 8px 0 2px; font-size: 0.86em; color: #7d4357; }
.gd-mini b { color: #9c3a5a; }
.gd-note { margin: 8px 0 0; font-size: 0.82em; font-style: italic; color: var(--read-text-faint,#888); line-height: 1.5; }
.gd-years { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0; }
.gd-year { padding: 5px 12px; background: #eef9f0; border: 1px solid #b6dfc0; border-radius: 16px; font-size: 0.88em; }
.gd-year b { color: #2e7d32; }
.gd-tuoi { display: flex; flex-wrap: wrap; gap: 10px; margin: 6px 0; font-size: 0.88em; }
.gd-tuoi .ok { color: #2e7d32; } .gd-tuoi .warn { color: #b06a28; }
.gd-year.dam { background: #ffeef5; border-color: #e09ab8; } .gd-year.dam b { color: #9c3a5a; }
.gd-card.gd-hit { background: #eef9f0; border-color: #b6dfc0; }
.gd-card.gd-hit h5 { color: #2e7d32; }
/* Lời văn ấm */
.gd-soft-btn { padding: 9px 18px; border: 1.5px solid #c98aa0; border-radius: 20px; background: transparent; color: #9c3a5a; font: inherit; font-size: 0.9em; cursor: pointer; transition: all .15s; }
.gd-soft-btn:hover { background: #9c3a5a; color: #fff; }
.gd-tho-card { text-align: center; }
.gd-tho { white-space: pre-wrap; text-align: left; line-height: 1.85; color: var(--read-text,#3a3a38); font-size: 0.95em; margin-top: 8px; }
.gd-share { text-align: center; margin: 12px 0; }
/* So nhiều người */
.gd-other-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.gd-x { padding: 6px 10px; border: 1px solid #e0b0bd; border-radius: 8px; background: #fff; color: #c0392b; cursor: pointer; }
.gd-add { display: block; margin: 4px 0 0; padding: 6px 14px; border: 1px dashed #c98aa0; border-radius: 16px; background: transparent; color: #9c3a5a; font: inherit; font-size: 0.85em; cursor: pointer; }
.gd-rank { display: flex; gap: 12px; align-items: flex-start; padding: 12px; margin: 8px 0; background: #fdf6f8; border: 1px solid #ecd7df; border-radius: 12px; }
.gd-rank-no { flex: none; width: 30px; height: 30px; border-radius: 50%; background: #9c3a5a; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.gd-rank-body { flex: 1; }
.gd-rank-top { display: flex; align-items: center; gap: 8px; }
.gd-rank-score { font-size: 1.3em; font-weight: 700; color: #9c3a5a; }
.gd-ung { font-size: 0.78em; color: #2e7d32; background: #eef9f0; padding: 1px 8px; border-radius: 10px; }
.gd-rank-muc { font-size: 0.85em; color: #7d4357; margin: 2px 0; }
.gd-rank-k { font-size: 0.82em; color: var(--read-text-faint,#777); }

/* Công cụ Xem tuổi đôi lứa */
.gd-tool { margin: 0 0 30px; padding: 22px; background: var(--read-surface,#fff); border: 1px solid #e8cdd6; border-radius: 16px; }
.gd-tool h3 { margin: 0 0 4px; color: #9c3a5a; font-size: 1.3em; text-align: center; }
.gd-tool-sub { margin: 0 0 16px; text-align: center; color: var(--read-text-faint,#777); font-size: 0.9em; }
.gd-form { display: flex; align-items: stretch; gap: 12px; flex-wrap: wrap; }
.gd-person { flex: 1; min-width: 210px; display: flex; flex-direction: column; gap: 8px; padding: 12px; background: #fdf6f8; border-radius: 10px; }
.gd-person h4 { margin: 0 0 2px; color: #7d2c47; font-size: 0.95em; }
.gd-in { padding: 8px 10px; border: 1px solid #dcc6cd; border-radius: 8px; font: inherit; font-size: 0.9em; background: #fff; color: #333; }
.gd-heart { display: flex; align-items: center; font-size: 1.6em; }
.gd-run { display: block; width: 100%; margin-top: 14px; padding: 12px; border: none; border-radius: 24px; background: #9c3a5a; color: #fff; font: inherit; font-size: 1em; cursor: pointer; transition: all .15s; }
.gd-run:hover:not(:disabled) { background: #7d2c47; }
.gd-run:disabled { opacity: .5; cursor: not-allowed; }
.gd-err { color: #c0392b; text-align: center; margin-top: 10px; font-size: 0.9em; }

.gd-result { margin-top: 22px; }
.gd-score { text-align: center; margin-bottom: 16px; }
.gd-score-num { font-size: 3em; font-weight: 700; color: #9c3a5a; line-height: 1; }
.gd-score-num span { font-size: 0.35em; color: #b88; font-weight: 400; }
.gd-score-muc { color: #7d4357; font-size: 1.02em; margin-top: 4px; }
.gd-truc { padding: 12px 16px; border-radius: 10px; margin-bottom: 14px; font-size: 0.94em; }
.gd-truc.ung { background: #eef9f0; border: 1px solid #b6dfc0; }
.gd-truc.chua { background: #fbf6ee; border: 1px solid #e6d6b8; }
.gd-truc b { color: #9c3a5a; text-transform: capitalize; }
.gd-truc-gt { margin-top: 6px; color: var(--read-text,#444); font-size: 0.92em; line-height: 1.55; }
.gd-he { display: flex; justify-content: center; gap: 18px; margin-bottom: 16px; font-size: 0.9em; color: #7d4357; }
.gd-he b { color: #9c3a5a; font-size: 1.1em; }
.gd-cols { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.gd-col { flex: 1; min-width: 230px; padding: 12px 14px; border-radius: 10px; }
.gd-col.khoa { background: #eef9f0; border: 1px solid #c4e6cd; }
.gd-col.giu { background: #fdf3ec; border: 1px solid #ecd3bf; }
.gd-col h5 { margin: 0 0 8px; font-size: 0.95em; }
.gd-col.khoa h5 { color: #2e7d32; } .gd-col.giu h5 { color: #b06a28; }
.gd-col ul { margin: 0; padding-left: 18px; } .gd-col li { margin: 6px 0; font-size: 0.88em; line-height: 1.5; color: var(--read-text,#3a3a38); }
.gd-giaquy { padding: 14px 16px; background: #f5f0fa; border: 1px solid #d8cce8; border-radius: 10px; margin-bottom: 14px; }
.gd-giaquy h5 { margin: 0 0 8px; color: #6a4a9c; }
.gd-giaquy ol { margin: 0; padding-left: 20px; } .gd-giaquy li { margin: 6px 0; font-size: 0.9em; line-height: 1.55; }
.gd-guide summary { cursor: pointer; color: #8a6d1a; font-size: 0.9em; padding: 6px 0; }
.gd-guide ul { padding-left: 18px; } .gd-guide li { margin: 6px 0; font-size: 0.86em; color: var(--read-text-faint,#777); line-height: 1.5; }
.gd-para { font-style: italic; color: #9c3a5a; font-size: 0.88em; margin-top: 8px; }

.gd-book-toggle { margin-top: 24px; border-top: 1px solid #ecd7df; padding-top: 14px; }
.gd-book-toggle > summary { cursor: pointer; padding: 12px 16px; background: #fdf6f8; border: 1px solid #ecd7df; border-radius: 10px; color: #9c3a5a; font-size: 0.98em; list-style: none; }
.gd-book-toggle > summary::-webkit-details-marker { display: none; }
.gd-book-toggle > summary::before { content: '▸ '; color: #c98aa0; }
.gd-book-toggle[open] > summary::before { content: '▾ '; }
.gd-book-toggle > summary:hover { background: #fbeef2; }
.gd-body { line-height: 1.85; color: var(--read-text, #2b2b2b); font-size: var(--reading-scale, 1em); margin-top: 16px; }
.gd-body :deep(.gd-h1) { display: none; } /* tiêu đề sách đã ở hero */
.gd-body :deep(h3) { margin: 28px 0 10px; padding-top: 14px; border-top: 1px solid #eddfe4; color: #9c3a5a; font-size: 1.25em; }
.gd-body :deep(h4) { margin: 20px 0 8px; color: #7d4357; font-size: 1.08em; }
.gd-body :deep(h5) { margin: 16px 0 6px; color: #8a6d1a; font-size: 0.98em; }
.gd-body :deep(p) { margin: 12px 0; }
.gd-body :deep(blockquote) { margin: 16px 0; padding: 12px 18px; background: #fbf3f6; border-left: 3px solid #c98aa0; border-radius: 6px; color: #5d4450; font-style: italic; }
.gd-body :deep(table) { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.9em; }
.gd-body :deep(th), .gd-body :deep(td) { border: 1px solid #e6d5db; padding: 7px 10px; text-align: left; vertical-align: top; }
.gd-body :deep(th) { background: #f7e9ee; color: #7d2c47; }
.gd-body :deep(ul), .gd-body :deep(ol) { margin: 12px 0; padding-left: 22px; }
.gd-body :deep(li) { margin: 5px 0; }
.gd-body :deep(hr) { border: none; border-top: 1px dashed #d8c2c9; margin: 26px 0; }
.gd-body :deep(code) { background: #f3e8ec; padding: 1px 5px; border-radius: 4px; font-size: 0.88em; }
.gd-body :deep(strong) { color: #7d2c47; }

.gd-foot { margin-top: 28px; padding: 16px; background: #f7f3f0; border-radius: 12px; text-align: center; color: var(--read-text-faint,#777); font-size: 0.9em; }

/* #55 — khung Hôn nhân song phái (12 khía cạnh) */
.gd-songphai { margin-top: 18px; padding: 14px 16px; background: #faf6f8; border: 1px solid #ecd9e1; border-radius: 12px; }
.gd-songphai > summary { cursor: pointer; font-weight: 700; color: #7d2c47; }
.gd-sp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; margin: 14px 0; }
.gd-sp-cell { border: 1px solid #e7dde2; border-radius: 10px; padding: 10px; background: #fff; }
.gd-sp-cell.c-đồng_tham { border-color: #8bc4a0; background: #f3faf5; }
.gd-sp-cell.c-dị_tham { border-color: #e0b772; background: #fdf8ef; }
.gd-sp-head { display: flex; align-items: center; gap: 6px; }
.gd-sp-id { background: #7d2c47; color: #fff; border-radius: 50%; width: 20px; height: 20px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.72em; flex: none; }
.gd-sp-ten { flex: 1; font-weight: 600; font-size: 0.86em; }
.gd-sp-lead { font-size: 0.68em; padding: 1px 6px; border-radius: 6px; background: #eee; color: #555; flex: none; }
.gd-sp-lead.bat_tu { background: #e6eef7; color: #2c5a7d; }
.gd-sp-lead.tu_vi { background: #f3e8ec; color: #7d2c47; }
.gd-sp-body { margin-top: 7px; }
.gd-sp-concord { font-size: 0.74em; font-weight: 700; color: #555; }
.gd-sp-read { margin: 4px 0 0; font-size: 0.82em; color: #444; }
.gd-sp-cross { margin: 3px 0 0; font-size: 0.78em; color: #777; }
.gd-sp-uns { color: #b08; opacity: 0.6; font-size: 0.72em; }
.gd-sp-skel { opacity: 0.5; }
.gd-sp-open { margin-top: 6px; }

/* 💍 Tình duyên (nữ mệnh) */
.gd-td { font-size: var(--reading-scale, 1em); }
.gd-td-who { text-align: center; margin: 4px 0 12px; font-size: 0.88em; color: var(--read-text-faint, #7d4357); }
.gd-td-who b { color: #9c3a5a; }
.gd-td-stage { background: #f3faf5; border-color: #c4e6cd; }
.gd-td-stage h5 { color: #2e7d32; }
.gd-td-quote { margin: 8px 0 0; font-style: italic; color: var(--read-text, #5d4450); font-size: 0.92em; line-height: 1.6; }
.gd-td-prof { margin: 10px 0; padding: 10px 12px; background: var(--read-surface, #fff); border: 1px solid #ecd7df; border-radius: 10px; }
.gd-td-prof-h { color: #9c3a5a; font-size: 0.96em; }
.gd-td-prof-h small { color: var(--read-text-faint, #999); font-weight: 400; }
.gd-td-kv { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.gd-td-tag { font-size: 0.76em; padding: 2px 8px; border-radius: 10px; background: #f3e8ec; color: #7d2c47; }
.gd-td-tag.ok { background: #eef9f0; color: #2e7d32; }
.gd-td-tag.warn { background: #fdf3ec; color: #b06a28; }
.gd-td-line { margin: 8px 0; padding: 8px 10px; border-left: 2px solid #ecd7df; }
.gd-td-line b { color: #9c3a5a; }
.gd-td-line b.gd-td-warn, .gd-td-warn { color: #b06a28 !important; }
.gd-do-text { margin: 6px 0 0; font-size: 0.86em; color: #2e7d32; line-height: 1.55; }
.gd-td-recon { background: #f7f3fb; border-color: #ddd0ea; }
.gd-td-recon h5 { color: #6a4a9c; }
.gd-td-recon-row { margin: 10px 0; padding: 10px 12px; background: var(--read-surface, #fff); border: 1px solid #e3d8ef; border-radius: 10px; }
.gd-td-recon-h { font-weight: 700; color: #6a4a9c; font-size: 0.92em; margin-bottom: 4px; }
.gd-td-pill { font-size: 0.72em; padding: 1px 7px; border-radius: 8px; margin-right: 5px; }
.gd-td-pill.tv { background: #f3e8ec; color: #7d2c47; }
.gd-td-pill.bt { background: #e6eef7; color: #2c5a7d; }
.gd-td-cach { margin: 8px 0; padding: 10px 12px; border-radius: 10px; border: 1px solid #ecd7df; background: var(--read-surface, #fff); }
.gd-td-cach.cc-the_manh { border-color: #c4e6cd; background: #f3faf5; }
.gd-td-cach.cc-diem_can_chu_y { border-color: #ecd3bf; background: #fdf6ef; }
.gd-td-cach-h { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.gd-td-cach-h b { color: #9c3a5a; }
.gd-td-cach-tag { font-size: 0.72em; padding: 1px 8px; border-radius: 10px; background: #eee; color: #555; }
.gd-td-cach-tag.cc-the_manh { background: #eef9f0; color: #2e7d32; }
.gd-td-cach-tag.cc-diem_can_chu_y { background: #fdf3ec; color: #b06a28; }
.gd-td-cach-pt { font-size: 0.72em; color: #7d2c47; background: #f3e8ec; padding: 1px 8px; border-radius: 10px; }
.gd-td-thoi { background: #fbf6ee; border-color: #e6d6b8; }
.gd-td-thoi h5 { color: #8a6d1a; }
.gd-td-narr-h { font-weight: 700; color: #9c3a5a; margin-bottom: 6px; }

/* ⭐ KHỐI CHẨN ĐOÁN CẤP ĐỘ (KILLER) */
.gd-cd { background: linear-gradient(165deg, var(--read-surface, #fffaf7), #fbeef2); border: 1.5px solid #e09ab8; box-shadow: 0 2px 14px rgba(156,58,90,0.08); }
.gd-cd-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }
.gd-cd-badge { display: inline-block; padding: 6px 14px; border-radius: 18px; background: #9c3a5a; color: #fff; font-size: 0.92em; font-weight: 600; }
.gd-cd-badge b { font-weight: 700; }
.gd-cd-badge.lv-1 { background: #2e7d32; } .gd-cd-badge.lv-2 { background: #5d9e3a; }
.gd-cd-badge.lv-3 { background: #b8862a; } .gd-cd-badge.lv-4 { background: #c06a28; }
.gd-cd-badge.lv-5 { background: #9c3a5a; }
.gd-cd-dots { display: flex; gap: 5px; }
.gd-cd-dot { width: 12px; height: 12px; border-radius: 50%; background: #e6d2da; border: 1px solid #d3aebd; }
.gd-cd-dot.on { background: #9c3a5a; border-color: #9c3a5a; }
.gd-cd-summary { margin: 4px 0 6px; font-size: 0.96em; color: var(--read-text, #5d4450); }
.gd-cd-summary b { color: #9c3a5a; font-size: 1.15em; }
.gd-cd-class { font-style: italic; color: #7d4357; }
.gd-cd-sec { margin: 12px 0 0; }
.gd-cd-h { margin: 0 0 5px; font-size: 0.9em; font-weight: 700; color: #7d2c47; }
.gd-cd-signals { margin: 0; padding-left: 18px; }
.gd-cd-signals li { margin: 4px 0; font-size: 0.88em; color: var(--read-text, #3a3a38); line-height: 1.5; }
.gd-cd-steps { list-style: none; margin: 0; padding: 0; }
.gd-cd-steps li { display: flex; gap: 8px; align-items: flex-start; margin: 6px 0; padding: 8px 10px; background: var(--read-surface, #fff); border: 1px solid #c4e6cd; border-radius: 8px; font-size: 0.9em; color: var(--read-text, #2e7d32); line-height: 1.5; }
.gd-cd-check { flex: none; color: #2e7d32; font-weight: 700; }
.gd-cd-ren { margin: 8px 0; padding: 8px 10px; background: var(--read-surface, #fff); border-left: 3px solid #c98aa0; border-radius: 6px; }
.gd-cd-ren-from { color: var(--read-text-faint, #999); } .gd-cd-ren-arrow { margin: 0 6px; color: #9c3a5a; }
.gd-cd-ren-to { font-weight: 700; color: #9c3a5a; }
.gd-cd-vang { margin: 14px 0 0; padding: 10px 14px; background: #fbf3f6; border-left: 3px solid #9c3a5a; border-radius: 6px; font-style: italic; font-size: 0.94em; color: var(--read-text, #5d4450); line-height: 1.6; }

/* KHỐI HỎI–ĐÁP THEO TUỔI */
.gd-cht-item { margin: 12px 0; padding: 12px; background: var(--read-surface, #fff); border: 1px solid #ecd7df; border-radius: 10px; }
.gd-cht-q { display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
.gd-cht-text { font-weight: 600; font-size: 0.92em; color: var(--read-text, #3a3a38); }
.gd-cht-he { flex: none; font-size: 0.7em; padding: 2px 8px; border-radius: 8px; background: #eee; color: #555; }
.gd-cht-he.he-tu_vi { background: #f3e8ec; color: #7d2c47; }
.gd-cht-he.he-bat_tu { background: #e6eef7; color: #2c5a7d; }
.gd-cht-he.he-mai_hoa { background: #eef9f0; color: #2e7d32; }
.gd-cht-a { margin-top: 6px; }
.gd-cht-a p { margin: 0; font-size: 0.9em; color: var(--read-text, #444); line-height: 1.55; }
.gd-cht-dotin { display: inline-block; margin-top: 5px; font-size: 0.74em; color: var(--read-text-faint, #999); }
.gd-cht-gieo { margin-top: 8px; }
.gd-gieo-box { margin-top: 8px; }
.gd-gieo-ta { width: 100%; resize: vertical; box-sizing: border-box; }
.gd-gieo-actions { display: flex; gap: 10px; align-items: center; margin-top: 8px; }
.gd-gieo-run { width: auto; margin-top: 0; padding: 9px 20px; }

/* Kết quả quẻ */
.gd-que { margin-top: 12px; padding: 12px 14px; background: #faf6f8; border: 1px solid #e3d0d9; border-radius: 10px; }
.gd-que-cauhoi { margin: 0 0 10px; font-style: italic; color: #7d2c47; font-size: 0.92em; }
.gd-que-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 8px; }
.gd-que-cell { display: flex; flex-direction: column; gap: 2px; padding: 8px 10px; background: var(--read-surface, #fff); border: 1px solid #ecd7df; border-radius: 8px; text-align: center; }
.gd-que-tag { font-size: 0.7em; color: var(--read-text-faint, #999); text-transform: uppercase; letter-spacing: 0.5px; }
.gd-que-cell b { color: #9c3a5a; font-size: 1.02em; }
.gd-que-cell small { color: var(--read-text-faint, #aaa); font-size: 0.75em; }
.gd-que-td { margin-top: 10px; }
.gd-que-quanhe { font-weight: 700; color: #6a4a9c; }
.gd-que-buoc { margin-top: 10px; }
.gd-que-buoc summary { color: #7d2c47; }
.gd-que-buoc-item { margin: 8px 0; padding-left: 4px; }
.gd-que-tam { margin-top: 10px; }

/* KHỐI LUẬN CHI TIẾT 12+10 */
.gd-qt { padding: 0; overflow: hidden; }
.gd-qt-sum { cursor: pointer; padding: 14px 16px; color: #9c3a5a; font-weight: 700; font-size: 0.98em; list-style: none; }
.gd-qt-sum::-webkit-details-marker { display: none; }
.gd-qt[open] .gd-qt-sum { border-bottom: 1px solid #ecd7df; }
.gd-qt > *:not(summary) { margin-left: 16px; margin-right: 16px; }
.gd-qt > *:last-child { margin-bottom: 14px; }
.gd-qt-tong { margin: 14px 16px; padding: 10px 14px; background: #f5f0fa; border-left: 3px solid #6a4a9c; border-radius: 6px; font-size: 0.92em; color: var(--read-text, #5d4450); line-height: 1.6; }
.gd-qt-rank { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 16px; }
.gd-qt-rank-grp { flex: 1; min-width: 180px; padding: 10px 12px; border-radius: 8px; background: var(--read-surface, #fff); border: 1px solid #ecd7df; }
.gd-qt-rank-grp.xh-truc_tiep { border-color: #c4e6cd; background: #f3faf5; }
.gd-qt-rank-grp.xh-gian_tiep { border-color: #d8cce8; background: #f7f3fb; }
.gd-qt-rank-grp.xh-tiem_an { border-color: #e6d6b8; background: #fbf6ee; }
.gd-qt-rank-grp ul { margin: 4px 0 0; padding-left: 18px; }
.gd-qt-rank-grp li { margin: 4px 0; font-size: 0.84em; color: var(--read-text, #444); line-height: 1.5; }
.gd-qt-sub { margin: 10px 16px; }
.gd-qt-sub > summary { cursor: pointer; color: #7d2c47; font-size: 0.92em; font-weight: 600; padding: 6px 0; }
.gd-qt-step { margin: 8px 0; padding: 8px 10px; background: var(--read-surface, #fff); border: 1px solid #ecd7df; border-radius: 8px; }
.gd-qt-step-h { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.gd-qt-step-h b { color: #9c3a5a; font-size: 0.9em; }
.gd-qt-step-h small { color: var(--read-text-faint, #999); }
.gd-qt-no { flex: none; width: 22px; height: 22px; border-radius: 50%; background: #9c3a5a; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 0.74em; font-weight: 700; }
.gd-qt-muc { margin-left: auto; font-size: 0.72em; color: var(--read-text-faint, #999); }
.gd-qt-step .gd-mini { margin: 6px 0 0; }
</style>
