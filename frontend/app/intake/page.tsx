'use client'

export default function IntakePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <a href="/" className="text-blue-600 hover:underline">
            ← Back to Home
          </a>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">
            Submit an Incident
          </h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">
            Incident Details
          </h2>

          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <textarea
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe what happened..."
                disabled
              />
              <p className="text-sm text-gray-500 mt-1">
                Not implemented yet
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Screenshot
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-md p-4 text-center text-gray-500">
                  Coming soon
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Log File
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-md p-4 text-center text-gray-500">
                  Coming soon
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email (optional)
              </label>
              <input
                type="email"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
                disabled
              />
            </div>

            <button
              type="submit"
              disabled
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Submit Incident
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}
