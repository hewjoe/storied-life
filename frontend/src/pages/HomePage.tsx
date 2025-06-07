import { Link } from 'react-router-dom'
import { HeartIcon, BookOpenIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

export default function HomePage() {
  const features = [
    {
      name: 'Digital Memorials',
      description: 'Create beautiful, lasting memorials to honor and remember your loved ones.',
      icon: HeartIcon,
      href: '/memorials',
    },
    {
      name: 'Share Stories',
      description: 'Preserve precious memories and stories for future generations.',
      icon: BookOpenIcon,
      href: '/stories',
    },
    {
      name: 'AI Conversations',
      description: 'Chat with AI personas based on the stories and memories shared.',
      icon: ChatBubbleLeftRightIcon,
      href: '/chat',
    },
  ]

  return (
    <div className="bg-white">
      {/* Hero section */}
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
          <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-blue-600 to-purple-600 opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" />
        </div>
        
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Preserving memories.{' '}
              <span className="text-blue-600">Honoring legacies.</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Create digital memorials, share stories, and keep the memory of your loved ones alive 
              through our AI-powered platform. Every story matters. Every memory counts.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/memorials"
                className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              >
                Create Memorial
              </Link>
              <Link
                to="/stories"
                className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600"
              >
                Browse Stories <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
        
        <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]">
          <div className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-blue-600 to-purple-600 opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]" />
        </div>
      </div>

      {/* Features section */}
      <div className="py-24 bg-gray-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-blue-600">Everything you need</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Keep memories alive forever
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Our platform provides all the tools you need to create meaningful digital memorials, 
              share precious stories, and connect with the memories of those you love.
            </p>
          </div>
          
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3 lg:gap-y-16">
              {features.map((feature) => (
                <div key={feature.name} className="relative pl-16">
                  <dt className="text-base font-semibold leading-7 text-gray-900">
                    <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
                      <feature.icon className="h-6 w-6 text-white" aria-hidden="true" />
                    </div>
                    {feature.name}
                  </dt>
                  <dd className="mt-2 text-base leading-7 text-gray-600">
                    {feature.description}
                  </dd>
                  <dd className="mt-4">
                    <Link
                      to={feature.href}
                      className="text-sm font-semibold text-blue-600 hover:text-blue-500"
                    >
                      Learn more →
                    </Link>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="bg-blue-600">
        <div className="px-6 py-24 sm:px-6 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Start preserving memories today
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-blue-100">
              Join families around the world who are keeping their loved ones' stories alive. 
              Create your first memorial and begin the journey of remembrance.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/memorials"
                className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-blue-600 shadow-sm hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                Get started
              </Link>
              <Link
                to="/stories"
                className="text-sm font-semibold leading-6 text-white hover:text-blue-100"
              >
                View examples <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 