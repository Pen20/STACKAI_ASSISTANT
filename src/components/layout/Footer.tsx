import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-white py-12 border-t border-slate-200">
      <div className="container mx-auto px-4 flex flex-col items-center text-center">
        
        {/* Personal Branding */}
        <div className="mb-6 space-y-2">
          <h2 className="text-2xl font-bold text-slate-900">
            Dogbalou Motognon Wastalas d&#39;Assise
          </h2>
          <p className="text-lg font-medium text-slate-600">
            PhD Student in Applied Data Science & AI
          </p>
        </div>

        {/* Links */}
        <div className="flex items-center gap-4 text-slate-500 mb-8">
          <Link 
            href="https://sites.google.com/view/dogbaloumotognonwastalas" 
            target="_blank" 
            className="hover:text-blue-600 hover:underline transition-colors"
          >
            Personal Website
          </Link>
          <span>•</span>
          <a 
            href="mailto:wastalasdassise@gmail.com" 
            className="hover:text-blue-600 transition-colors"
          >
            wastalasdassise@gmail.com
          </a>
        </div>

        {/* Divider */}
        <div className="w-full max-w-md border-t border-slate-100 my-2"></div>

        {/* Copyright & Credits */}
        <div className="mt-8 space-y-1 text-sm text-slate-400">
          <p>
            &copy; {new Date().getFullYear()} Dogbalou Motognon. All rights reserved.
          </p>
          <p>
            Powered by OpenAI & Convex
          </p>
        </div>

      </div>
    </footer>
  );
}
