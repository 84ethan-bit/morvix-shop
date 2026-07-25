# 🎨 MORVIX Design System v1.0

> **"웹툰, 숏폼 에이전트, 커머스 모음집, 어드민 OS 전체를 아우르는 통일된 브랜드 visual & UI 가이드라인"**

---

## 1. 디자인 철학 (Design Philosophy)

* **Cyber Glassmorphism:** 차세대 AI 에이전트 플랫폼에 어울리는 스페이스 다크 톤과 네온 글래스 효과
* **Situation-First Empathy:** 강렬한 시각적 억까 탈출 쿨링 블루 및 파이어 핫 컬러를 통해 심리적 공감대 극대화
* **Consistent Brand Experience:** 웹툰 프레임, 숏폼 서체, 쇼핑몰 랜딩 및 어드민 컴포넌트 간 일관성 유지

---

## 2. 디자인 토큰 스펙 (Design Tokens)

### 🎨 Color Palette
- **Background Main (`--bg-main`):** `#0a0d14` (Deep Space Dark)
- **Background Card (`--bg-card`):** `rgba(22, 27, 38, 0.75)` (Glassmorphism Blur)
- **Primary Accent (`--primary-accent`):** `#00f2fe` ➔ `#4facfe` (Cyber Cyan Gradient)
- **Highlight Red (`--highlight-red`):** `#ff4757` (HOT Badge & Discount Rate)
- **Success Green (`--success-green`):** `#2ed573` (Conversion & Verified Badge)
- **Text Main (`--text-main`):** `#f1f5f9` (High Contrast White)
- **Text Muted (`--text-muted`):** `#94a3b8` (Subtle Text)
- **Border Color (`--border-color`):** `rgba(255, 255, 255, 0.08)`

---

## 3. 타이포그래피 (Typography)

* **Primary Body:** `Inter`, -apple-system, sans-serif
* **Brand Headings & Badges:** `Outfit`, sans-serif (Bold 700 / 900)
* **Code & Slug Display:** `Fira Code`, `Courier New`, monospace

---

## 4. 컴포넌트 규격 (Component Guidelines)

### 🔘 Buttons
- **Primary CTA (`.btn-coupang-cta`):** Full-width, Linear Gradient (`#ff4757` ➔ `#ff6b81`), Glow Hover Animation
- **Category Filter (`.category-btn`):** Pill-shape (`border-radius: 50px`), Glass Effect with Cyan Border on active

### 🎴 Cards & Containers
- **Product Card (`.product-card`):** Border Radius 16px, Backdrop Filter `blur(12px)`, Hover Elevation `translateY(-4px)`
- **Modal Overlay (`.modal-overlay`):** Backdrop `rgba(0,0,0,0.8)`, Centered Smooth Fade-in

### 📏 Spacing & Radius Tokens
- `--radius-sm`: `8px`
- `--radius-md`: `14px`
- `--radius-lg`: `24px`
- `--shadow-glass`: `0 8px 32px 0 rgba(0, 0, 0, 0.37)`
