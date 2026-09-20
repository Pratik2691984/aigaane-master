import Head from "next/head";
import ProsodyLab from "../components/ProsodyLab";

export default function ProsodyPage() {
  return (
    <>
      <Head>
        <title>Piṅgala Prosody Lab | aigaane.in</title>
        <meta name="description" content="Computational Sanskrit prosody scansion and Pingala Chandas verification engine." />
      </Head>
      <main className="min-h-screen bg-slate-950 py-12 px-4 sm:px-6 lg:px-8">
        <ProsodyLab />
      </main>
    </>
  );
}
