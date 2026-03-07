const OrnamentalDivider = ({ title }: { title: string }) => (
  <div className="my-10">
    <div className="ornamental-divider">
      <span className="font-display text-sm tracking-[0.3em] uppercase text-primary">
        ✦ {title} ✦
      </span>
    </div>
  </div>
);

export default OrnamentalDivider;
