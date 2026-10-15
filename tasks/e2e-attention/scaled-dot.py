from manim import *

NARRATION = [
    "This one line is the whole mechanism: attention of Q, K and V equals softmax of Q times K transposed, divided by the square root of d k, then times V.",
    "First, Q times K transposed gives one score for every pair of a query and a key, which says how well they match.",
    "Next we divide by the square root of d k. With d k equal to sixty four, the raw scores spread out by sixty four, so dividing by eight keeps them in a range where the softmax can still learn.",
    "Then the softmax turns the scores into weights that add up to one, and multiplying by V blends the values using those weights.",
]

class Scaled(Scene):
    def construct(self):
        title = Text("Scaled dot-product attention", font_size=40, weight=BOLD).to_corner(UL, buff=0.6)
        formula = MathTex(r"\mathrm{Attention}(Q,K,V)", r"=", r"\mathrm{softmax}\!\left(\frac{QK^{T}}{\sqrt{d_k}}\right)", r"V").scale(1.15).shift(1.5 * UP)

        def box(tex, color):
            m = MathTex(tex, font_size=34, color=color)
            return VGroup(RoundedRectangle(corner_radius=0.15, width=m.width + 0.7, height=1.0, color=color), m)

        row = VGroup(box(r"QK^{T}", YELLOW), box(r"\div \sqrt{d_k}", BLUE), box(r"\mathrm{softmax}", GREEN), box(r"\times V", PURPLE)).arrange(RIGHT, buff=1.0).shift(0.3 * DOWN)
        arrows = [Arrow(a.get_right(), b.get_left(), buff=0.1, color=GREY) for a, b in zip(row[:-1], row[1:])]
        tags = [Text(t, font_size=24, color=c).next_to(b, DOWN, buff=0.3) for t, c, b in
                zip(["match scores", "keep it tame", "make weights", "blend values"], [YELLOW, BLUE, GREEN, PURPLE], row)]
        num = MathTex(r"d_k = 64 \;\Rightarrow\; \sqrt{d_k} = 8", font_size=36, color=BLUE).shift(2.6 * DOWN)
        self.add(title)
        with self.voice(1):
            self.play(Write(formula), run_time=3)
        with self.voice(2):
            self.play(FadeIn(row[0]), FadeIn(tags[0]))
            self.play(Circumscribe(row[0], color=YELLOW))
        with self.voice(3):
            self.play(GrowArrow(arrows[0]), FadeIn(row[1]), FadeIn(tags[1]))
            self.play(Write(num))
        with self.voice(4):
            self.play(FadeOut(num))
            self.play(GrowArrow(arrows[1]), FadeIn(row[2]), FadeIn(tags[2]))
            self.play(GrowArrow(arrows[2]), FadeIn(row[3]), FadeIn(tags[3]))
