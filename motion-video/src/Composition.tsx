import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Tajawal";

const { fontFamily } = loadFont("normal", {
  weights: ["800", "900"],
  subsets: ["arabic", "latin"],
});

// ===== 4 flat colors only =====
const INK = "#1B1B1B";
const CREAM = "#F3E9D2";
const RED = "#E63B2E";
const YELLOW = "#FFC845";

const W = 1080;
const H = 1920;
const FPS = 30;
const DURATION = 600; // 20s

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ===== Board layout: station centers in board coordinates =====
type Station = { x: number; y: number; rot: number };
const A: Station = { x: 900, y: 1200, rot: 0 };
const B: Station = { x: 2800, y: 1200, rot: 0 };
const C: Station = { x: 2800, y: 3800, rot: -90 }; // laid sideways; camera rolls 90°
const D: Station = { x: 900, y: 3800, rot: 0 };
const E: Station = { x: 2060, y: 6400, rot: 0 };
const OVERVIEW = { x: 2060, y: 3800 };
const BOARD_W = 4200;
const BOARD_H = 7800;

// ===== Camera keyframes =====
type Cam = { f: number; x: number; y: number; r: number; s: number };
const WHIP = Easing.bezier(0.75, 0, 0.15, 1);
const DRIFT = Easing.inOut(Easing.sin);
const KEYS: (Cam & { ease?: (t: number) => number })[] = [
  { f: 0, x: A.x, y: A.y, r: 0, s: 1.06 },
  { f: 80, x: A.x, y: A.y, r: 0, s: 1.0, ease: DRIFT },
  { f: 100, x: B.x, y: B.y, r: -4, s: 1.0, ease: WHIP }, // fast whip + tilt
  { f: 190, x: B.x, y: B.y, r: -2, s: 1.04, ease: DRIFT },
  { f: 222, x: C.x, y: C.y, r: 90, s: 1.0, ease: WHIP }, // 90° roll
  { f: 330, x: C.x, y: C.y, r: 90, s: 1.03, ease: DRIFT },
  { f: 356, x: D.x, y: D.y, r: 0, s: 1.0, ease: WHIP },
  { f: 445, x: D.x, y: D.y, r: 0, s: 1.04, ease: DRIFT },
  { f: 470, x: E.x, y: E.y, r: 0, s: 1.0, ease: WHIP },
  { f: 545, x: E.x, y: E.y, r: 0, s: 1.02, ease: DRIFT },
  { f: 585, x: OVERVIEW.x, y: OVERVIEW.y, r: 0, s: 0.245, ease: Easing.bezier(0.6, 0, 0.2, 1) },
  { f: DURATION, x: OVERVIEW.x, y: OVERVIEW.y, r: 0, s: 0.24, ease: DRIFT },
];

const cameraAt = (frame: number): Cam => {
  let i = 0;
  while (i < KEYS.length - 2 && frame > KEYS[i + 1].f) i++;
  const a = KEYS[i];
  const b = KEYS[i + 1];
  const t = interpolate(frame, [a.f, b.f], [0, 1], { ...clamp, easing: b.ease });
  const lerp = (p: number, q: number) => p + (q - p) * t;
  return { f: frame, x: lerp(a.x, b.x), y: lerp(a.y, b.y), r: lerp(a.r, b.r), s: lerp(a.s, b.s) };
};

// ===== Shared text style =====
const txt = (size: number, color: string, weight = 900): React.CSSProperties => ({
  fontFamily,
  fontWeight: weight,
  fontSize: size,
  lineHeight: 1.25,
  color,
  direction: "rtl",
  whiteSpace: "nowrap",
});

const Num: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style,
}) => (
  <span dir="ltr" style={{ direction: "ltr", unicodeBidi: "isolate", display: "inline-block", ...style }}>
    {children}
  </span>
);

// Centered row placed at a y (top) inside a station
const Row: React.FC<{ y: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  y,
  children,
  style,
}) => (
  <div
    style={{
      position: "absolute",
      top: y,
      left: 0,
      width: W,
      display: "flex",
      justifyContent: "center",
      ...style,
    }}
  >
    {children}
  </div>
);

// ===== Kashida stretch: right+ZWJ | clipped scaled tatweel | ZWJ+left =====
const Kashida: React.FC<{
  right: string;
  left: string;
  width: number;
  size: number;
  color: string;
  shadow?: string;
}> = ({ right, left, width, size, color, shadow }) => {
  const lh = size * 1.25;
  const k = width / (size * 0.18) + 2; // overscale, box clips it
  const base: React.CSSProperties = { ...txt(size, color), lineHeight: `${lh}px`, textShadow: shadow };
  return (
    <div style={{ display: "flex", flexDirection: "row", direction: "rtl", alignItems: "flex-start" }}>
      <span style={base}>{right + "‍"}</span>
      <div style={{ width, height: lh, overflow: "hidden", flexShrink: 0 }}>
        <div style={{ ...base, textShadow: "none", width, textAlign: "center", transform: `scaleX(${k})` }}>
          ـ
        </div>
      </div>
      <span style={base}>{"‍" + left}</span>
    </div>
  );
};

// ===== Panel on the board =====
const Panel: React.FC<{ st: Station; bg: string; shadow: string; children: React.ReactNode }> = ({
  st,
  bg,
  shadow,
  children,
}) => (
  <div
    style={{
      position: "absolute",
      left: st.x - W / 2,
      top: st.y - H / 2,
      width: W,
      height: H,
      transform: `rotate(${st.rot}deg)`,
      transformOrigin: "center",
    }}
  >
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: bg,
        boxShadow: `40px 40px 0 ${shadow}`,
        overflow: "hidden",
      }}
    >
      {children}
    </div>
  </div>
);

// ===== Station A: «عرض» kashida + «محلّي» bounce =====
const StationA: React.FC<{ frame: number }> = ({ frame }) => {
  const { fps } = useVideoConfig();
  const stretch = spring({ frame: frame - 2, fps, config: { damping: 14, stiffness: 60 } });
  const kw = interpolate(stretch, [0, 1], [70, 330]);

  // drop + squash
  const drop = interpolate(frame, [6, 16], [-560, 0], { ...clamp, easing: Easing.in(Easing.quad) });
  const rebound = interpolate(frame, [16, 22, 28], [0, -50, 0], {
    ...clamp,
    easing: Easing.inOut(Easing.quad),
  });
  const squash = interpolate(frame, [15, 18, 24, 30], [0, 1, -0.3, 0], clamp);
  const sy = 1 - 0.28 * squash;
  const sx = 1 + 0.2 * squash;
  const landOpacity = interpolate(frame, [6, 8], [0, 1], clamp);

  const pill = spring({ frame: frame - 34, fps, config: { damping: 11 } });

  return (
    <>
      <Row y={360}>
        <Kashida right="ع" left="رض" width={kw} size={300} color={INK} shadow={`10px 10px 0 ${RED}`} />
      </Row>
      <Row y={790}>
        <div
          style={{
            ...txt(220, RED),
            textShadow: `10px 10px 0 ${INK}`,
            opacity: landOpacity,
            transform: `translateY(${drop + rebound}px) scale(${sx}, ${sy})`,
            transformOrigin: "50% 100%",
          }}
        >
          محلّي
        </div>
      </Row>
      <Row y={1140}>
        <div
          style={{
            ...txt(64, CREAM, 800),
            background: INK,
            padding: "6px 44px 14px",
            transform: `scale(${pill})`,
          }}
        >
          لفترة محدودة
        </div>
      </Row>
    </>
  );
};

// ===== Word swap helper (old goes up, new comes from below) =====
const Swap: React.FC<{
  frame: number;
  at: number;
  height: number;
  oldEl: React.ReactNode;
  newEl: React.ReactNode;
}> = ({ frame, at, height, oldEl, newEl }) => {
  const t = interpolate(frame, [at, at + 12], [0, 1], { ...clamp, easing: Easing.bezier(0.7, 0, 0.3, 1) });
  return (
    <div style={{ position: "relative", height, width: W, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          transform: `translateY(${-t * height}px)`,
        }}
      >
        {oldEl}
      </div>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          transform: `translateY(${(1 - t) * height}px)`,
        }}
      >
        {newEl}
      </div>
    </div>
  );
};

// ===== Station B: strike old price, swap to new =====
const StationB: React.FC<{ frame: number }> = ({ frame }) => {
  const strike = interpolate(frame, [118, 130], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const priceStyle = (c: string): React.CSSProperties => ({
    ...txt(300, c),
    textShadow: `10px 10px 0 ${c === RED ? INK : YELLOW}`,
    display: "flex",
    alignItems: "center",
    gap: 30,
  });
  const riyal = <span style={{ ...txt(110, INK, 800), textShadow: "none" }}>ريال</span>;

  return (
    <>
      <Row y={360}>
        <Swap
          frame={frame}
          at={150}
          height={190}
          oldEl={<div style={txt(140, INK)}>كان سعره</div>}
          newEl={<div style={txt(140, INK)}>صار بس</div>}
        />
      </Row>
      <Row y={620}>
        <Swap
          frame={frame}
          at={152}
          height={420}
          oldEl={
            <div style={priceStyle(INK)}>
              <div style={{ position: "relative" }}>
                <Num>200</Num>
                <div
                  style={{
                    position: "absolute",
                    left: -20,
                    right: -20,
                    top: "52%",
                    height: 34,
                    background: RED,
                    transform: `rotate(-8deg) scaleX(${strike})`,
                    transformOrigin: "left center",
                  }}
                />
              </div>
              {riyal}
            </div>
          }
          newEl={
            <div style={priceStyle(RED)}>
              <Num>100</Num>
              {riyal}
            </div>
          }
        />
      </Row>
      <Row y={1120}>
        <div style={{ ...txt(72, INK, 800), opacity: interpolate(frame, [160, 170], [0, 1], clamp) }}>
          نفس الطعم.. نص السعر
        </div>
      </Row>
    </>
  );
};

// ===== Station C: ink fill «خصم» + counter + dot burst =====
const StationC: React.FC<{ frame: number }> = ({ frame }) => {
  const { fps } = useVideoConfig();
  const fill = interpolate(frame, [212, 245], [0, 100], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const n = Math.round(
    interpolate(frame, [232, 275], [0, 50], { ...clamp, easing: Easing.out(Easing.cubic) }),
  );
  const pop = spring({ frame: frame - 275, fps, config: { damping: 8, stiffness: 180 } });
  const pulse = frame >= 275 ? 1 + 0.18 * Math.sin(pop * Math.PI) : 1;
  const burst = interpolate(frame, [275, 300], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const word: React.CSSProperties = { ...txt(320, CREAM), lineHeight: "400px" };

  const dots = Array.from({ length: 18 }, (_, i) => {
    const ang = (i / 18) * Math.PI * 2;
    const dist = (300 + (i % 3) * 90) * burst;
    const size = (i % 2 ? 34 : 24) * (1 - burst * 0.9);
    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: 540 + Math.cos(ang) * dist * 1.25 - size / 2,
          top: 1010 + Math.sin(ang) * dist - size / 2,
          width: size,
          height: size,
          borderRadius: "50%",
          background: i % 3 === 0 ? CREAM : i % 3 === 1 ? YELLOW : INK,
          opacity: burst > 0 && burst < 1 ? 1 : 0,
        }}
      />
    );
  });

  return (
    <>
      <Row y={340}>
        <div style={{ position: "relative" }}>
          <div style={{ ...word, color: "transparent", WebkitTextStroke: `6px ${CREAM}` }}>خصم</div>
          <div
            style={{
              ...word,
              position: "absolute",
              inset: 0,
              textShadow: `12px 12px 0 ${INK}`,
              clipPath: `inset(${100 - fill}% -40px -40px -40px)`,
            }}
          >
            خصم
          </div>
        </div>
      </Row>
      {dots}
      <Row y={790}>
        <div style={{ ...txt(360, YELLOW), textShadow: `14px 14px 0 ${INK}`, transform: `scale(${pulse})` }}>
          <Num>{n}%</Num>
        </div>
      </Row>
    </>
  );
};

// ===== Station D: swap «بكرة؟» → «اليوم بس» + highlight + selection box =====
const StationD: React.FC<{ frame: number }> = ({ frame }) => {
  const hl = interpolate(frame, [392, 404], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const sel = interpolate(frame, [404, 412], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2)) });
  const handle = (pos: React.CSSProperties, i: number) => (
    <div
      key={i}
      style={{
        position: "absolute",
        width: 34,
        height: 34,
        background: CREAM,
        border: `6px solid ${RED}`,
        ...pos,
      }}
    />
  );
  return (
    <>
      <Row y={380}>
        <div style={txt(120, INK)}>العرض متى؟</div>
      </Row>
      <Row y={640}>
        <div style={{ position: "relative" }}>
          {/* highlight sits behind the swap row */}
          <div
            style={{
              position: "absolute",
              left: 110,
              right: 110,
              top: 150,
              height: 150,
              background: YELLOW,
              transform: `scaleX(${hl}) rotate(-2deg)`,
              transformOrigin: "right center",
            }}
          />
          <Swap
            frame={frame}
            at={378}
            height={360}
            oldEl={<div style={{ ...txt(200, INK), lineHeight: "360px" }}>بكرة؟</div>}
            newEl={<div style={{ ...txt(200, INK), lineHeight: "360px" }}>اليوم بس</div>}
          />
          {/* selection frame with handles */}
          <div
            style={{
              position: "absolute",
              left: 70,
              right: 70,
              top: 30,
              bottom: 20,
              border: `6px solid ${RED}`,
              opacity: sel > 0 ? 1 : 0,
              transform: `scale(${1.15 - 0.15 * sel})`,
            }}
          >
            {[
              { left: -23, top: -23 },
              { right: -23, top: -23 },
              { left: -23, bottom: -23 },
              { right: -23, bottom: -23 },
            ].map(handle)}
          </div>
        </div>
      </Row>
      <Row y={1130}>
        <div
          style={{
            ...txt(80, CREAM, 800),
            background: RED,
            padding: "4px 44px 14px",
            opacity: interpolate(frame, [414, 420], [0, 1], clamp),
          }}
        >
          وبكرة يرجع السعر
        </div>
      </Row>
    </>
  );
};

// ===== Station E: curtain pulled by rope reveals the offer =====
const StationE: React.FC<{ frame: number }> = ({ frame }) => {
  const pull = interpolate(frame, [474, 482, 490], [0, 1, 0.2], { ...clamp, easing: Easing.inOut(Easing.quad) });
  const open = interpolate(frame, [482, 508], [0, 1], { ...clamp, easing: Easing.bezier(0.6, 0, 0.2, 1) });
  const cardPop = interpolate(frame, [496, 512], [0.88, 1], { ...clamp, easing: Easing.out(Easing.back(2.5)) });
  const top = 230;
  const bottom = 1360;
  const curtain = (side: "l" | "r") => {
    const sign = side === "l" ? -1 : 1;
    const stripes = Array.from({ length: 6 }, (_, i) => (
      <div
        key={i}
        style={{ position: "absolute", top: 0, bottom: 0, left: 40 + i * 85, width: 10, background: INK, opacity: 1 }}
      />
    ));
    return (
      <div
        style={{
          position: "absolute",
          top,
          height: bottom - top,
          width: W / 2 + 10,
          left: side === "l" ? 0 : W / 2 - 10,
          background: RED,
          overflow: "hidden",
          transformOrigin: side === "l" ? "left center" : "right center",
          transform: `translateX(${sign * open * 120}px) scaleX(${1 - open * 0.9})`,
        }}
      >
        {stripes}
      </div>
    );
  };
  return (
    <>
      {/* the offer card (behind the curtain) */}
      <div
        style={{
          position: "absolute",
          left: 70,
          right: 110,
          top: 300,
          bottom: 1920 - 1290,
          background: INK,
          transform: `scale(${cardPop})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={txt(100, CREAM)}>على كل المنيو</div>
        <div style={{ ...txt(380, YELLOW), lineHeight: 1.05, textShadow: `14px 14px 0 ${RED}` }}>
          <Num>50%</Num>
        </div>
        <div style={{ ...txt(90, INK), background: YELLOW, padding: "0 50px 10px", marginTop: 20 }}>
          اليوم بس
        </div>
      </div>
      {curtain("l")}
      {curtain("r")}
      {/* teaser text on the curtain */}
      <Row y={640} style={{ opacity: 1 - interpolate(frame, [482, 490], [0, 1], clamp) }}>
        <div style={{ ...txt(170, CREAM), textShadow: `10px 10px 0 ${INK}` }}>جاهز؟</div>
      </Row>
      {/* rod */}
      <div style={{ position: "absolute", left: 30, right: 30, top: top - 30, height: 36, background: INK }} />
      {/* rope + knob */}
      <div
        style={{
          position: "absolute",
          left: 1025,
          top: top,
          width: 10,
          height: 520 + pull * 140,
          background: YELLOW,
          border: `4px solid ${INK}`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 1000,
          top: top + 510 + pull * 140,
          width: 60,
          height: 80,
          borderRadius: 30,
          background: YELLOW,
          border: `6px solid ${INK}`,
        }}
      />
    </>
  );
};

// ===== Main =====
export const MyComponent: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = cameraAt(frame);
  return (
    <AbsoluteFill style={{ background: INK, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: BOARD_W,
          height: BOARD_H,
          transformOrigin: `${cam.x}px ${cam.y}px`,
          transform: `translate(${W / 2 - cam.x}px, ${H / 2 - cam.y}px) rotate(${cam.r}deg) scale(${cam.s})`,
        }}
      >
        <Panel st={A} bg={YELLOW} shadow={RED}>
          <StationA frame={frame} />
        </Panel>
        <Panel st={B} bg={CREAM} shadow={YELLOW}>
          <StationB frame={frame} />
        </Panel>
        <Panel st={C} bg={RED} shadow={YELLOW}>
          <StationC frame={frame} />
        </Panel>
        <Panel st={D} bg={CREAM} shadow={RED}>
          <StationD frame={frame} />
        </Panel>
        <Panel st={E} bg={CREAM} shadow={YELLOW}>
          <StationE frame={frame} />
        </Panel>
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => {
  return (
    <Composition
      id="MyComp"
      component={MyComponent}
      durationInFrames={DURATION}
      fps={FPS}
      width={W}
      height={H}
    />
  );
};
