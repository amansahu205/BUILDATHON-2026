import { Scale, ArrowRight, Shield, Brain, Eye, MessageSquare, Zap, TrendingUp, Clock, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useEffect, useRef, useCallback, useState } from "react";

/* ─── Data ─── */
const AGENTS = [
  { icon: MessageSquare, name: "Interrogation Engine", desc: "AI-powered opposing counsel simulation with adaptive questioning strategies" },
  { icon: Eye, name: "Objection Copilot", desc: "Real-time FRE objection detection with rule citations and training notes" },
  { icon: Brain, name: "Inconsistency Detector", desc: "Cross-references live testimony against all case documents instantly" },
  { icon: Shield, name: "Behavioral Sentinel", desc: "Facial micro-expression analysis for composure coaching and readiness" },
];

const STATS = [
  { value: 60, suffix: "%", label: "Prep Time Reduction" },
  { value: 3, suffix: "x", label: "Witness Confidence" },
  { value: 94, suffix: "%", label: "Consistency Rate" },
  { value: 500, suffix: "+", label: "Cases Coached" },
];

const MARQUEE_ITEMS = [
  "Timeline Analysis", "Financial Discovery", "Prior Sworn Statements", "Communications Review",
  "Behavioral Coaching", "Objection Training", "Cross-Reference Engine", "Impeachment Prevention",
  "Timeline Analysis", "Financial Discovery", "Prior Sworn Statements", "Communications Review",
  "Behavioral Coaching", "Objection Training", "Cross-Reference Engine", "Impeachment Prevention",
];

const TESTIMONIALS = [
  { quote: "VERDICT cut our witness prep time by 60% while improving deposition scores across the board.", author: "Sarah Chen", title: "Partner, Morrison & Associates" },
  { quote: "The inconsistency detection alone has prevented three potential impeachments this quarter.", author: "James Rivera", title: "Senior Litigator, Drake & Partners" },
  { quote: "We've never had a witness this confident walking into a deposition. Game-changing technology.", author: "Elena Vasquez", title: "Trial Attorney, Blackwell LLP" },
];

const WORKFLOW_STEPS = [
  { icon: Zap, title: "Upload Case Documents", desc: "Drag & drop depositions, discovery, and prior statements. AI indexes everything in minutes." },
  { icon: Users, title: "Configure Witness Session", desc: "Set focus areas, aggression level, and enable AI agents tailored to your case strategy." },
  { icon: TrendingUp, title: "Run Practice Deposition", desc: "AI opposing counsel adapts in real-time. Alerts flag inconsistencies and objections live." },
  { icon: Clock, title: "Review Coaching Brief", desc: "Detailed scoring, weakness maps, and actionable coaching recommendations delivered instantly." },
];

/* ─── Hooks ─── */
function useIntersectionObserver(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

function useCountUp(target: number, visible: boolean, duration = 1500) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!visible) return;
    let start = 0;
    const step = target / (duration / 16);
    const id = setInterval(() => {
      start += step;
      if (start >= target) { setCount(target); clearInterval(id); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(id);
  }, [target, visible, duration]);
  return count;
}

/* ─── Custom Cursor ─── */
function CustomCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const pos = useRef({ x: 0, y: 0 });
  const lerped = useRef({ x: 0, y: 0 });
  const hovering = useRef(false);

  useEffect(() => {
    const onMove = (e: MouseEvent) => { pos.current = { x: e.clientX, y: e.clientY }; };
    const onOver = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      hovering.current = !!t.closest("a, button, [role='button']");
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseover", onOver);

    let raf: number;
    const loop = () => {
      lerped.current.x += (pos.current.x - lerped.current.x) * 0.15;
      lerped.current.y += (pos.current.y - lerped.current.y) * 0.15;
      if (cursorRef.current) {
        cursorRef.current.style.transform = `translate(${lerped.current.x - 16}px, ${lerped.current.y - 16}px)`;
        cursorRef.current.classList.toggle("hovering", hovering.current);
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => { window.removeEventListener("mousemove", onMove); window.removeEventListener("mouseover", onOver); cancelAnimationFrame(raf); };
  }, []);

  return <div ref={cursorRef} className="custom-cursor hidden md:block" />;
}

/* ─── Particle Canvas ─── */
function ParticleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let w = (canvas.width = window.innerWidth);
    let h = (canvas.height = window.innerHeight);
    const particles: { x: number; y: number; vy: number; vx: number; r: number; a: number }[] = [];

    for (let i = 0; i < 80; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vy: -(Math.random() * 0.4 + 0.1),
        vx: (Math.random() - 0.5) * 0.2,
        r: Math.random() * 2 + 0.5,
        a: Math.random() * 0.5 + 0.1,
      });
    }

    let raf: number;
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.y < -10) { p.y = h + 10; p.x = Math.random() * w; }
        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(38, 92%, 50%, ${p.a})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(draw);
    };
    draw();

    const onResize = () => { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; };
    window.addEventListener("resize", onResize);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", onResize); };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />;
}

/* ─── Counter Card ─── */
function CounterCard({ value, suffix, label, visible, delay }: { value: number; suffix: string; label: string; visible: boolean; delay: number }) {
  const count = useCountUp(value, visible);
  return (
    <div
      className="glass rounded-xl p-6 text-center opacity-0 animate-fade-up"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "forwards" }}
    >
      <p className="text-4xl md:text-5xl font-display font-bold text-gradient-gold">
        {count}{suffix}
      </p>
      <p className="text-sm text-muted-foreground mt-2">{label}</p>
    </div>
  );
}

/* ─── Main Page ─── */
const LandingPage = () => {
  const heroObs = useIntersectionObserver(0.1);
  const statsObs = useIntersectionObserver(0.2);
  const agentsObs = useIntersectionObserver(0.1);
  const workflowObs = useIntersectionObserver(0.1);
  const testimonialsObs = useIntersectionObserver(0.1);

  return (
    <div className="min-h-screen bg-background overflow-hidden cursor-none md:cursor-none">
      <CustomCursor />

      {/* ─── Nav ─── */}
      <header className="fixed top-0 w-full z-50 glass-strong">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="h-7 w-7 text-primary" />
            <span className="font-display text-xl font-bold text-gradient-gold tracking-wide">VERDICT</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" className="cursor-none" asChild>
              <Link to="/login">Log In</Link>
            </Button>
            <Button className="bg-gradient-gold text-primary-foreground shadow-gold cursor-none" asChild>
              <Link to="/login">Request Demo</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* ─── Hero with Particles + Orbs ─── */}
      <section ref={heroObs.ref} className="relative pt-32 pb-24 px-4 min-h-[90vh] flex items-center">
        <ParticleCanvas />

        {/* Orbs */}
        <div className="orb w-[500px] h-[500px] -top-40 -left-40 bg-primary/20" />
        <div className="orb w-[400px] h-[400px] top-1/3 -right-32 bg-verdict-blue/15" style={{ animationDelay: "2s" }} />
        <div className="orb w-[300px] h-[300px] bottom-0 left-1/3 bg-verdict-gold/10" style={{ animationDelay: "4s" }} />

        <div className="container max-w-5xl text-center relative z-10">
          {/* Staggered entrance */}
          <p
            className={`font-serif italic text-lg md:text-xl text-muted-foreground mb-4 opacity-0 ${heroObs.visible ? "animate-fade-up stagger-1" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            AI-Powered Deposition Coaching
          </p>
          <h1
            className={`font-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold leading-[0.95] mb-8 opacity-0 ${heroObs.visible ? "animate-fade-up stagger-2" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            From <span className="text-gradient-gold">16 hours</span>
            <br className="hidden sm:block" /> to{" "}
            <span className="text-gradient-gold">6 hours</span>
            <br className="hidden sm:block" /> per witness
          </h1>
          <p
            className={`text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto opacity-0 ${heroObs.visible ? "animate-fade-up stagger-3" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            Find inconsistencies, flag objections, and prepare your witnesses before opposing counsel does.
          </p>
          <div
            className={`flex items-center justify-center gap-4 opacity-0 ${heroObs.visible ? "animate-fade-up stagger-4" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            <Button size="lg" className="bg-gradient-gold text-primary-foreground shadow-gold text-base px-8 cursor-none" asChild>
              <Link to="/login">
                Request Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-base px-8 cursor-none" asChild>
              <Link to="/login">Log In</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ─── Marquee ─── */}
      <div className="border-y border-border/50 bg-verdict-surface py-4 overflow-hidden">
        <div className="marquee-track">
          {MARQUEE_ITEMS.map((item, i) => (
            <span key={i} className="inline-flex items-center gap-3 px-8 text-sm font-medium text-muted-foreground whitespace-nowrap">
              <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* ─── Stats — Counter animations on intersection ─── */}
      <section ref={statsObs.ref} className="py-24 px-4">
        <div className="container">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            {STATS.map((s, i) => (
              <CounterCard key={s.label} {...s} visible={statsObs.visible} delay={i * 150} />
            ))}
          </div>
        </div>
      </section>

      {/* ─── Bento Grid — Asymmetric 5/4/3 spans ─── */}
      <section ref={agentsObs.ref} className="py-24 bg-verdict-surface relative px-4">
        <div className="container">
          <h2
            className={`font-display text-4xl md:text-5xl font-bold text-center mb-4 opacity-0 ${agentsObs.visible ? "animate-fade-up" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            Four AI Agents. One Platform.
          </h2>
          <p
            className={`font-serif italic text-muted-foreground text-center mb-16 text-lg opacity-0 ${agentsObs.visible ? "animate-fade-up" : ""}`}
            style={{ animationDelay: "100ms", animationFillMode: "forwards" }}
          >
            Specialized intelligence working in concert during every session.
          </p>

          {/* Bento: 12-col grid with asymmetric spans */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-5">
            {AGENTS.map((agent, i) => {
              // Asymmetric: 5/7 then 7/5
              const span = i === 0 ? "md:col-span-5" : i === 1 ? "md:col-span-7" : i === 2 ? "md:col-span-7" : "md:col-span-5";
              return (
                <div
                  key={agent.name}
                  className={`${span} glass rounded-2xl p-8 group hover:border-primary/30 transition-all duration-300 hover:scale-[1.02] opacity-0 ${agentsObs.visible ? "animate-fade-up" : ""}`}
                  style={{ animationDelay: `${(i + 1) * 120}ms`, animationFillMode: "forwards" }}
                >
                  <agent.icon className="h-10 w-10 text-primary mb-5 group-hover:scale-110 transition-transform" />
                  <h3 className="font-display text-xl font-bold mb-2">{agent.name}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">{agent.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─── Scrollytelling Workflow ─── */}
      <section ref={workflowObs.ref} className="py-24 px-4">
        <div className="container max-w-4xl">
          <h2
            className={`font-display text-4xl md:text-5xl font-bold text-center mb-4 opacity-0 ${workflowObs.visible ? "animate-fade-up" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            How It Works
          </h2>
          <p
            className={`font-serif italic text-muted-foreground text-center mb-16 text-lg opacity-0 ${workflowObs.visible ? "animate-fade-up" : ""}`}
            style={{ animationDelay: "100ms", animationFillMode: "forwards" }}
          >
            From documents to deposition-ready in four steps.
          </p>

          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-6 md:left-8 top-0 bottom-0 w-px bg-border" />

            <div className="space-y-12">
              {WORKFLOW_STEPS.map((step, i) => (
                <ScrollyPanel key={step.title} index={i} parentVisible={workflowObs.visible}>
                  <div className="flex items-start gap-6 md:gap-8 pl-2">
                    <div className="relative z-10 shrink-0 w-12 h-12 md:w-16 md:h-16 rounded-full glass flex items-center justify-center border border-primary/20">
                      <step.icon className="h-5 w-5 md:h-6 md:w-6 text-primary" />
                    </div>
                    <div className="pt-1">
                      <span className="text-xs font-mono text-primary mb-1 block">STEP 0{i + 1}</span>
                      <h3 className="font-display text-xl md:text-2xl font-bold mb-2">{step.title}</h3>
                      <p className="text-muted-foreground text-sm md:text-base leading-relaxed">{step.desc}</p>
                    </div>
                  </div>
                </ScrollyPanel>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ─── Testimonials ─── */}
      <section ref={testimonialsObs.ref} className="py-24 bg-verdict-surface px-4">
        <div className="container max-w-5xl">
          <h2
            className={`font-display text-4xl md:text-5xl font-bold text-center mb-16 opacity-0 ${testimonialsObs.visible ? "animate-fade-up" : ""}`}
            style={{ animationFillMode: "forwards" }}
          >
            Trusted by Top Litigators
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <div
                key={t.author}
                className={`glass rounded-2xl p-8 opacity-0 ${testimonialsObs.visible ? "animate-fade-up" : ""}`}
                style={{ animationDelay: `${i * 150}ms`, animationFillMode: "forwards" }}
              >
                <p className="font-serif italic text-foreground mb-6 leading-relaxed">"{t.quote}"</p>
                <div>
                  <p className="font-semibold text-sm">{t.author}</p>
                  <p className="text-xs text-muted-foreground">{t.title}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section className="py-32 px-4 relative">
        <div className="orb w-[600px] h-[600px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary/10" />
        <div className="container max-w-3xl text-center relative z-10">
          <h2 className="font-display text-4xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Witness Prep?
          </h2>
          <p className="text-lg text-muted-foreground mb-10 max-w-xl mx-auto">
            Join leading litigation teams using AI to prepare witnesses faster and more effectively than ever.
          </p>
          <Button size="lg" className="bg-gradient-gold text-primary-foreground shadow-gold text-base px-10 cursor-none" asChild>
            <Link to="/login">
              Request Demo <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="border-t border-border py-8 px-4">
        <div className="container flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Scale className="h-4 w-4 text-primary" />
            <span className="font-display tracking-wide">VERDICT © 2026</span>
          </div>
          <p className="font-serif italic">Enterprise AI for Litigation</p>
        </div>
      </footer>
    </div>
  );
};

/* ─── Scrollytelling Panel (IntersectionObserver) ─── */
function ScrollyPanel({ children, index, parentVisible }: { children: React.ReactNode; index: number; parentVisible: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!parentVisible) return;
    const el = ref.current;
    if (!el) return;
    const timer = setTimeout(() => {
      const obs = new IntersectionObserver(
        ([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } },
        { threshold: 0.3 }
      );
      obs.observe(el);
      return () => obs.disconnect();
    }, index * 100);
    return () => clearTimeout(timer);
  }, [parentVisible, index]);

  return (
    <div ref={ref} className={`scrolly-panel ${visible ? "visible" : ""}`}>
      {children}
    </div>
  );
}

export default LandingPage;
