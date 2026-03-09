import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="border-t border-primary/20 px-6 py-10 md:px-12 lg:px-24">
      <div className="mx-auto max-w-4xl text-center">
        <p className="font-body text-sm leading-relaxed text-muted-foreground">
          Data sourced from World Bank, FRED, IMF, and regional central banks.
        </p>

        <p className="mt-6 font-mono-data text-xs text-muted-foreground/60">
          Built with Python · Claude API · GitHub Actions
          {" · "}
          <a
            href="https://plausible.io/"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-primary"
          >
            Privacy-friendly analytics by Plausible
          </a>
        </p>
        <Link
          to="/archive"
          className="mt-2 inline-block font-mono-data text-xs text-muted-foreground/40 transition-colors hover:text-primary"
        >
          Browse Past Issues
        </Link>
      </div>

      {/* Geometric border strip */}
      <div className="geometric-border-bottom mt-8" />
    </footer>
  );
};

export default Footer;
