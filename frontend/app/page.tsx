export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            🛡️ Rubrica SRE Agent
          </h1>
          <p className="text-gray-600">
            Autonomous Incident Intake & Triage
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">
              Submit an Incident
            </h2>
            <p className="text-gray-600 mb-4">
              Report an issue with screenshot and logs for automated triage.
            </p>
            <a
              href="/intake"
              className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Start Report
            </a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">
              View Dashboard
            </h2>
            <p className="text-gray-600 mb-4">
              Check the status of your submitted incidents.
            </p>
            <button
              disabled
              className="inline-block bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed"
            >
              Coming Soon
            </button>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 p-6 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">
            🚧 Under Construction
          </h3>
          <p className="text-blue-800">
            This is the initial skeleton. Full implementation coming soon.
          </p>
        </div>
      </main>
    </div>
  )
}
