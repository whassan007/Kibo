import React, { useState } from 'react'
import { Play, RotateCcw, AlertTriangle, CheckSquare, Info } from 'lucide-react'
import { DeployabilityLadder } from '../components/DeployabilityLadder'
import type { RungType } from '../components/DeployabilityLadder'
import { WMethodStack } from '../components/WMethodStack'

export const Tutorial: React.FC = () => {
  const [activeStep, setActiveStep] = useState(1)
  const [simProposalCreated, setSimProposalCreated] = useState(false)
  const [boundaryViolation, setBoundaryViolation] = useState(false)
  const [simProposalStatus, setSimProposalStatus] = useState<'idle' | 'proposed' | 'promoted' | 'halted'>('idle')
  const [version, setVersion] = useState('5.1.0')
  const [ladderRung, setLadderRung] = useState<RungType>('waël-only')

  const resetSimulation = () => {
    setSimProposalCreated(false)
    setBoundaryViolation(false)
    setSimProposalStatus('idle')
    setVersion('5.1.0')
    setLadderRung('waël-only')
  }

  const triggerProposal = () => {
    setSimProposalCreated(true)
    if (boundaryViolation) {
      setSimProposalStatus('halted')
    } else {
      setSimProposalStatus('proposed')
    }
  }

  const handlePromote = () => {
    if (simProposalStatus === 'proposed') {
      setSimProposalStatus('promoted')
      setVersion('5.2.0')
      setLadderRung('agent-deployable')
    }
  }

  return (
    <div className="space-y-6 font-mono text-xs select-none animate-fade-in">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>7. Interactive System Tutorial</span>
          <span className="text-xs bg-bauhaus-accent text-bauhaus-black px-2 py-0.5 font-extrabold text-[10px]">Training Module</span>
        </h2>
        <button
          onClick={resetSimulation}
          className="text-bauhaus-lightgrey hover:text-bauhaus-white flex items-center space-x-1.5 border border-bauhaus-mediumgrey px-2 py-1 hover:bg-bauhaus-black"
        >
          <RotateCcw size={12} />
          <span className="text-[9px] uppercase font-bold tracking-wider">Reset Simulator</span>
        </button>
      </div>

      <p className="text-xs text-bauhaus-lightgrey leading-relaxed max-w-2xl">
        Welcome to the KIBO OS Interactive Training Ground. This module simulates how the operating system runs, evaluates boundaries, and climbs the deployability ladder. Follow the steps below to practice.
      </p>

      {/* Tutorial Navigation Steps */}
      <div className="grid grid-cols-4 border border-bauhaus-mediumgrey divide-x divide-bauhaus-mediumgrey text-center">
        {[
          { id: 1, label: '1. AGENT PROPOSAL' },
          { id: 2, label: '2. RUBRIC SCORING' },
          { id: 3, label: '3. HUMAN GATING' },
          { id: 4, label: '4. LADDER CLIMB' },
        ].map((step) => {
          const isActive = activeStep === step.id
          return (
            <button
              key={step.id}
              onClick={() => setActiveStep(step.id)}
              className={`py-3 font-bold uppercase text-[9px] tracking-wider transition-colors ${
                isActive ? 'bg-bauhaus-black text-bauhaus-accent border-b-2 border-b-bauhaus-accent' : 'bg-transparent text-bauhaus-lightgrey hover:text-bauhaus-white'
              }`}
            >
              {step.label}
            </button>
          )
        })}
      </div>

      {/* Main Simulation Sandbox Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left/Middle Column: Step Explanation & Interactive Simulation controls */}
        <div className="lg:col-span-2 space-y-6">
          {activeStep === 1 && (
            <div className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey space-y-4">
              <h3 className="text-base font-bold text-bauhaus-white uppercase tracking-tight">Step 1: The Core Loop - Agent Proposes</h3>
              <p className="text-bauhaus-lightgrey leading-relaxed text-[11px]">
                Under KIBO OS, agent crews perform the heavy lifting but operate with zero direct merge permissions. To modify any config, system prompt, or step, they must write a structured JSON proposal and submit it to your judgment queue.
              </p>
              
              <div className="p-3 bg-bauhaus-black border border-bauhaus-mediumgrey space-y-2">
                <span className="font-bold text-bauhaus-white block uppercase text-[9px]">Simulation Control Panel</span>
                <p className="text-[10px] text-bauhaus-lightgrey">
                  Simulate the <strong>Scout</strong> crew discovering target alignment and compiling an autonomy expansion request for `can_reach_out`.
                </p>
                <button
                  onClick={triggerProposal}
                  disabled={simProposalCreated}
                  className="flex items-center space-x-1.5 bg-bauhaus-accent text-bauhaus-black px-4 py-2 hover:bg-opacity-80 transition-opacity font-bold uppercase text-[10px] disabled:opacity-50"
                >
                  <Play size={12} />
                  <span>Request Crew Proposal</span>
                </button>
              </div>

              {simProposalCreated && (
                <div className="border border-bauhaus-accent p-3.5 bg-bauhaus-black space-y-2">
                  <div className="flex justify-between text-[9px] text-bauhaus-lightgrey uppercase">
                    <span>PROP-ID: prop_01hqscoutreach001</span>
                    <span className="text-bauhaus-yellow font-bold">STATUS: {simProposalStatus.toUpperCase()}</span>
                  </div>
                  <pre className="p-2.5 bg-bauhaus-grey border border-bauhaus-mediumgrey text-[10px] text-bauhaus-lightgrey leading-relaxed overflow-x-auto">
{`{
  "id": "prop_01hqscoutreach001",
  "target": "autonomy:scout:can_reach_out",
  "rationale": "Automate Acquire phase qualification stage to decrease manual gates.",
  "diff": "grants.json -> scout.can_reach_out from false to true",
  "expected_effect": {
    "cac": "-15% vs baseline $5,000",
    "gates_per_deployment": "-1"
  },
  "status": "proposed"
}`}
                  </pre>
                  <button
                    onClick={() => setActiveStep(2)}
                    className="text-bauhaus-accent hover:underline font-bold text-[10px]"
                  >
                    Proceed to Rubric Scoring Step &rarr;
                  </button>
                </div>
              )}
            </div>
          )}

          {activeStep === 2 && (
            <div className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey space-y-4">
              <h3 className="text-base font-bold text-bauhaus-white uppercase tracking-tight">Step 2: Rubric Scoring & Hard Stops</h3>
              <p className="text-bauhaus-lightgrey leading-relaxed text-[11px]">
                Before any proposal enters the judgment queue, it is automatically assessed against KIBO OS rubrics (§10.2). If <strong>Boundary Adherence</strong> or <strong>Claim Integrity</strong> fails, the pipeline immediately halts, blocking promotion.
              </p>

              <div className="p-3 bg-bauhaus-black border border-bauhaus-mediumgrey space-y-3">
                <span className="font-bold text-bauhaus-white block uppercase text-[9px]">Simulation Control Panel</span>
                <p className="text-[10px] text-bauhaus-lightgrey">
                  Toggle boundary violations to see the difference between a compliant proposal and a rogue crew action.
                </p>

                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer text-[10px]">
                    <input
                      type="radio"
                      checked={!boundaryViolation}
                      onChange={() => {
                        setBoundaryViolation(false)
                        if (simProposalCreated) setSimProposalStatus('proposed')
                      }}
                      className="accent-bauhaus-accent"
                    />
                    <span className="text-bauhaus-white">Compliant Sandbox Data</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer text-[10px]">
                    <input
                      type="radio"
                      checked={boundaryViolation}
                      onChange={() => {
                        setBoundaryViolation(true)
                        if (simProposalCreated) setSimProposalStatus('halted')
                      }}
                      className="accent-bauhaus-red"
                    />
                    <span className="text-bauhaus-red font-bold">Rogue External Cloud Route (Violation)</span>
                  </label>
                </div>
              </div>

              {simProposalCreated && boundaryViolation && (
                <div className="border border-bauhaus-red bg-bauhaus-red/10 p-4 text-bauhaus-red space-y-2">
                  <div className="flex items-center gap-2 font-bold uppercase text-[10px]">
                    <AlertTriangle size={14} />
                    <span>Pipeline halted: Hard-Stop Triggered</span>
                  </div>
                  <p className="text-[10px] leading-relaxed">
                    The proposal contains instructions violating §8 scope boundaries (routed client data to a public endpoint). Autonomy halted. No proposal has been emitted to the human queue. A failure report was appended to `feedback/log.md`.
                  </p>
                </div>
              )}

              {simProposalCreated && !boundaryViolation && (
                <div className="border border-bauhaus-accent p-3.5 bg-bauhaus-black space-y-2">
                  <div className="flex items-center gap-2 text-bauhaus-accent font-bold uppercase text-[10px]">
                    <CheckSquare size={14} />
                    <span>Rubric check passed: Ready for Human Gate</span>
                  </div>
                  <p className="text-[10px] text-bauhaus-lightgrey leading-relaxed">
                    Correctness (5/5), Boundary adherence (5/5), Claim integrity (5/5). Safe for human review.
                  </p>
                  <button
                    onClick={() => setActiveStep(3)}
                    className="text-bauhaus-accent hover:underline font-bold text-[10px]"
                  >
                    Proceed to Human Gating &rarr;
                  </button>
                </div>
              )}
            </div>
          )}

          {activeStep === 3 && (
            <div className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey space-y-4">
              <h3 className="text-base font-bold text-bauhaus-white uppercase tracking-tight">Step 3: The Human Gate - You Decide</h3>
              <p className="text-bauhaus-lightgrey leading-relaxed text-[11px]">
                Under KIBO OS, only the human owner (Waël Hassan) has promotion authorization. No proposal can commit code modifications without manual operator signature. Let's decide.
              </p>

              {!simProposalCreated ? (
                <div className="p-4 border border-dashed border-bauhaus-mediumgrey text-center text-bauhaus-lightgrey">
                  No proposal drafted. Go back to step 1 to trigger a simulated proposal first.
                </div>
              ) : simProposalStatus === 'halted' ? (
                <div className="border border-bauhaus-red bg-bauhaus-red/10 p-4 text-bauhaus-red">
                  Proposal halted in Step 2. Toggle "Compliant Sandbox Data" in Step 2 to clear the rubric failure.
                </div>
              ) : (
                <div className="border border-bauhaus-mediumgrey bg-bauhaus-black p-4 space-y-3">
                  <span className="font-bold text-bauhaus-white block uppercase text-[9px]">YOUR JUDGMENT QUEUE</span>
                  <div className="p-3 bg-bauhaus-grey border border-bauhaus-mediumgrey space-y-2">
                    <span className="font-bold text-bauhaus-white uppercase text-[10px] block">Target: autonomy:scout:can_reach_out</span>
                    <p className="text-[10px] text-bauhaus-lightgrey">
                      Expected effect: CAC decreases by 15%, manual gates reduced by 1 step.
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={handlePromote}
                        disabled={simProposalStatus === 'promoted'}
                        className="flex-1 bg-bauhaus-accent text-bauhaus-black py-2 font-bold uppercase text-[9px] hover:bg-opacity-80 transition-opacity"
                      >
                        {simProposalStatus === 'promoted' ? 'PROMOTED ✓' : 'PROMOTE'}
                      </button>
                      <button
                        onClick={() => setSimProposalStatus('idle')}
                        className="border border-bauhaus-red text-bauhaus-red px-4 py-2 font-bold uppercase text-[9px] hover:bg-bauhaus-red hover:text-bauhaus-black"
                      >
                        Reject
                      </button>
                    </div>
                  </div>

                  {simProposalStatus === 'promoted' && (
                    <button
                      onClick={() => setActiveStep(4)}
                      className="text-bauhaus-accent hover:underline font-bold text-[10px] block pt-2"
                    >
                      Proceed to Ladder Climb &rarr;
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {activeStep === 4 && (
            <div className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey space-y-4">
              <h3 className="text-base font-bold text-bauhaus-white uppercase tracking-tight">Step 4: Ladder Climb & Version Commit</h3>
              <p className="text-bauhaus-lightgrey leading-relaxed text-[11px]">
                Upon promotion, KIBO OS commits the versioned semver bump to the changelog file, modifies the active prompt, and progresses step owners up the Deployability Ladder (shifting manual checks to automated crew executions).
              </p>

              <div className="grid grid-cols-2 gap-4">
                <div className="border border-bauhaus-mediumgrey p-3 bg-bauhaus-black flex flex-col justify-between">
                  <span className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider block mb-1">Active Version</span>
                  <span className="text-3xl font-extrabold text-bauhaus-white tracking-tight">{version}</span>
                  <span className="text-[8px] text-bauhaus-accent uppercase font-bold mt-1">✓ CHANGELOG UPDATED</span>
                </div>
                <div className="border border-bauhaus-mediumgrey p-3 bg-bauhaus-black flex flex-col justify-between">
                  <span className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider block mb-1">Acquire Step Owner</span>
                  <span className="text-xl font-bold uppercase text-bauhaus-accent">{ladderRung === 'agent-deployable' ? 'Agent (Auto)' : 'Waël-Only (Manual)'}</span>
                  <span className="text-[8px] text-bauhaus-lightgrey uppercase font-bold mt-1">✓ LADDER CLIMB COMPLETED</span>
                </div>
              </div>

              {simProposalStatus !== 'promoted' && (
                <div className="p-3 border border-dashed border-bauhaus-mediumgrey text-bauhaus-lightgrey text-center">
                  Proposal not promoted yet. Go to step 3 and click "PROMOTE" to trigger the ladder climb.
                </div>
              )}

              {simProposalStatus === 'promoted' && (
                <div className="p-4 border border-bauhaus-accent bg-bauhaus-black text-center space-y-3">
                  <span className="font-bold text-bauhaus-accent block text-[10px] uppercase">✓ TRAINING COMPLETED</span>
                  <p className="text-[10px] text-bauhaus-lightgrey">
                    You have successfully completed the core improvement training module. Reset the simulator to practice again, or navigate to other tabs to manage live configs.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Visual locators illustrating simulations */}
        <div className="space-y-4">
          <WMethodStack activeLayer={activeStep === 1 ? 2 : activeStep === 2 ? 6 : activeStep === 4 ? 7 : undefined} />
          
          <DeployabilityLadder
            currentRung={ladderRung}
            transition={simProposalStatus === 'proposed' ? { before: 'waël-only', after: 'agent-deployable' } : undefined}
          />

          <div className="border border-bauhaus-mediumgrey p-4 bg-bauhaus-grey font-mono text-[9px] text-bauhaus-lightgrey leading-relaxed space-y-2 select-none">
            <div className="flex items-center gap-1.5 font-bold uppercase text-bauhaus-accent">
              <Info size={12} />
              <span>Sovereignty Note</span>
            </div>
            <p>
              Tutorial simulations do not write to the active client workspace files (`.kibo/`). They execute purely in local browser memory to demonstrate KIBO OS principles without risking production environments.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
