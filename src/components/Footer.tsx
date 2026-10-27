import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="border-t border-primary/20 px-6 py-10 md:px-12 lg:px-24">
      <div className="mx-auto max-w-4xl text-center">
        <p className="font-body text-sm leading-relaxed text-muted-foreground">
          Compiled every Monday from World Bank, FRED, Finnhub, NewsAPI and GDELT data. The analysis is written by Claude.
        </p>

        <p className="mt-4 font-body text-sm text-muted-foreground/70">
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
          className="mt-3 inline-block font-body text-sm text-primary/70 transition-colors hover:text-primary"
        >
          Browse past issues
        </Link>
      </div>

      {/* Geometric border strip */}
      <div className="geometric-border-bottom mt-8" />
    </footer>
  );
};

export default Footer;
