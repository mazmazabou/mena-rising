const OrnamentalDivider = ({ title }: { title: string }) => (
  <div className="mx-auto mb-8 mt-14 max-w-6xl">
    <h2 className="section-head font-display text-[1.7rem] font-medium italic leading-tight text-primary md:text-3xl">
      <svg viewBox="0 0 48 48" className="h-6 w-6 shrink-0 self-center" aria-hidden="true">
        <g fill="none" stroke="currentColor" strokeWidth="2.2">
          <rect x="12" y="12" width="24" height="24" />
          <rect x="12" y="12" width="24" height="24" transform="rotate(45 24 24)" />
        </g>
      </svg>
      {title}
    </h2>
  </div>
);

export default OrnamentalDivider;
