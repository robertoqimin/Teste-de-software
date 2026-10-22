import React, { Fragment } from 'react';

import { LogoutButton } from '../components/Navigation';
import { MutationForm } from '../components/MutationForm';
import { TabButton, TabPanel } from '../components/Tabs';
import { truthy } from '../utils';

export default function ProfessorPainel({ data }) {
    const { documentos = [], notas = [], professor = {}, solicitacoes_documentos = [], turmas = [] } = data;
    return <>

    <aside className="w-72 glass-sidebar h-screen sticky top-0 flex flex-col p-6">
        <div className="mb-10 text-center">
            <h2 className="text-xl font-bold tracking-tighter text-cyan-400">SECRETARIA DF</h2>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Portal do Professor</p>
        </div>

        <nav className="flex-1 space-y-2">
            <div className="text-[10px] font-bold text-gray-500 mb-2 ml-4">MINHA ÁREA</div>
            <TabButton type="button" group="professor" value="turmas" as="button" className="professor-nav-link w-full flex items-center px-4 py-3 rounded-xl">
                Turmas
            </TabButton>
            <TabButton type="button" group="professor" value="notas" as="button" className="professor-nav-link w-full flex items-center px-4 py-3 rounded-xl hover:bg-white/5 transition-all hover:text-white">
                Notas
            </TabButton>
            <TabButton type="button" group="professor" value="documentos" as="button" className="professor-nav-link w-full flex items-center px-4 py-3 rounded-xl hover:bg-white/5 transition-all hover:text-white">
                Documentos
            </TabButton>
        </nav>

        <div className="mt-auto pt-6 border-t border-white/10">
            <LogoutButton  className="flex items-center px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-all">
                Sair do Sistema
            </LogoutButton>
        </div>
    </aside>

    <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
            <div>
                <h1 className="text-3xl font-bold">Olá, Prof. {professor.nome}!</h1>
                <p className="text-gray-400">{professor.disciplina} · {professor.regime}</p>
            </div>
            <div className="flex items-center gap-4">
                <div className="text-right">
                    <p className="text-sm font-bold">{professor.email}</p>
                    <p className="text-[10px] text-cyan-400">PROF-{professor.id}</p>
                </div>
                {truthy(professor.foto_perfil) ? <> 
                <img src={`/arquivos/perfil/${encodeURIComponent(professor.foto_perfil)}`} alt={`Foto de ${professor.nome}`} className="w-12 h-12 rounded-full border-2 border-white/20 object-cover" />
                 </> : <> 
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 border-2 border-white/20"></div>
                 </>}
            </div>
        </header>

        <TabPanel group="professor" value="turmas" as="section" className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Turmas</h2>
                <span className="text-sm text-gray-400">Turmas associadas ao seu cadastro</span>
            </div>

            {turmas.length ? <>{turmas.map((turma, index30) => <Fragment key={turma?.id ?? index30}>
            <article className="glass-card professor-card rounded-[28px] p-6">
                <div className="flex flex-wrap items-start justify-between gap-4 mb-5">
                    <div>
                        <h3 className="text-lg font-bold text-cyan-400">{turma.nome}</h3>
                        <p className="text-sm text-gray-400">{turma.codigo} · {turma.ano_letivo} · {turma.turno}</p>
                    </div>
                    <span className="professor-pill">{turma.alunos.length} alunos</span>
                </div>

                <div className="mb-5">
                    <p className="text-xs uppercase tracking-wider text-gray-500 mb-2">Disciplinas nesta turma</p>
                    <div className="flex flex-wrap gap-2">
                        {turma.disciplinas.length ? <>{turma.disciplinas.map((disciplina, index31) => <Fragment key={disciplina?.id ?? index31}>
                        <span className="professor-chip">{disciplina.nome}</span>
                        </Fragment>)}</> : <>
                        <span className="text-sm text-gray-400">Nenhuma disciplina associada ao professor nesta turma.</span>
                        </>}
                    </div>
                </div>

                <div className="professor-activity-panel">
                    <div>
                        <h4>Lançar atividade</h4>
                        <p>Publique uma atividade para esta turma.</p>
                    </div>
                    {truthy(turma.disciplinas) ? <> 
                    <MutationForm action={"/api/professor/atividades/lancar"} method="post" encType="multipart/form-data" className="professor-activity-form">
                        <input type="hidden" name="turma_id" value={turma.id} />
                        <select name="disciplina_id" required>
                            {turma.disciplinas.map((disciplina, index32) => <Fragment key={disciplina?.id ?? index32}>
                            <option value={disciplina.id}>{disciplina.nome}</option>
                            </Fragment>)}
                        </select>
                        <input name="titulo" type="text" placeholder="Título da atividade" required />
                        <input name="data_entrega" type="date" />
                        <input name="arquivo" type="file" />
                        <textarea name="descricao" placeholder="Descrição da atividade"></textarea>
                        <button>Lançar atividade</button>
                    </MutationForm>
                     </> : <> 
                    <p className="text-sm text-gray-400">Associe uma disciplina ao professor e à turma para lançar atividade.</p>
                     </>}

                    <div className="professor-activity-list">
                        {turma.atividades.length ? <>{turma.atividades.map((atividade, index33) => <Fragment key={atividade?.id ?? index33}>
                        <article>
                            <div>
                                <strong>{atividade.titulo}</strong>
                                <span>{atividade.disciplina} · Entrega: {atividade.data_entrega}</span>
                                <p>{atividade.descricao}</p>
                                {truthy(atividade.arquivo) ? <> 
                                <a href={`/arquivos/download/${encodeURIComponent(atividade.arquivo)}`}>Baixar anexo</a>
                                 </> : <>  </>}
                            </div>
                            <small>{atividade.data}</small>
                        </article>
                        </Fragment>)}</> : <>
                        <div className="professor-empty-line">Nenhuma atividade lançada para esta turma.</div>
                        </>}
                    </div>
                </div>

                <div className="professor-table-wrapper">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-gray-500 text-xs uppercase tracking-wider">
                                <th className="pb-4 font-medium">Aluno</th>
                                <th className="pb-4 font-medium">Disciplina</th>
                                <th className="pb-4 font-medium">Nota</th>
                                <th className="pb-4 font-medium">Observação</th>
                                <th className="pb-4 font-medium"></th>
                            </tr>
                        </thead>
                        <tbody className="text-sm">
                            {turma.alunos.length ? <>{turma.alunos.map((aluno, index34) => <Fragment key={aluno?.id ?? index34}>
                            <tr className="border-t border-white/5">
                                <td className="py-4">
                                    <span className="block font-bold text-white">{aluno.nome}</span>
                                    <span className="text-xs text-gray-500">{aluno.matricula}</span>
                                </td>
                                <td className="py-4" colSpan="4">
                                    {truthy(turma.disciplinas) ? <> 
                                    <MutationForm action={"/api/professor/notas/salvar"} method="post" className="professor-grade-form">
                                        <input type="hidden" name="turma_id" value={turma.id} />
                                        <input type="hidden" name="aluno_id" value={aluno.id} />
                                        <select name="disciplina_id" required>
                                            {turma.disciplinas.map((disciplina, index35) => <Fragment key={disciplina?.id ?? index35}>
                                            <option value={disciplina.id}>{disciplina.nome}</option>
                                            </Fragment>)}
                                        </select>
                                        <input name="nota" type="number" min="0" max="10" step="0.01" placeholder="0-10" required />
                                        <input name="observacao" type="text" placeholder="Observação" />
                                        <button>Salvar nota</button>
                                    </MutationForm>
                                     </> : <> 
                                    <span className="text-gray-500">Associe uma disciplina ao professor e à turma para lançar nota.</span>
                                     </>}
                                </td>
                            </tr>
                            </Fragment>)}</> : <>
                            <tr className="border-t border-white/5">
                                <td className="py-6 text-gray-400" colSpan="5">Nenhum aluno associado a esta turma.</td>
                            </tr>
                            </>}
                        </tbody>
                    </table>
                </div>
            </article>
            </Fragment>)}</> : <>
            <div className="glass-card professor-card rounded-[28px] p-6 text-gray-400">
                Nenhuma turma associada ao seu cadastro.
            </div>
            </>}
        </TabPanel>

        <TabPanel group="professor" value="notas" as="section" className="">
            <div className="glass-card professor-card rounded-[32px] p-8 mb-8">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">Lançar Notas</h2>
                    <span className="text-sm text-gray-400">Por turma, aluno e disciplina</span>
                </div>

                <div className="space-y-5">
                    {turmas.length ? <>{turmas.map((turma, index36) => <Fragment key={turma?.id ?? index36}>
                    <article className="professor-doc-block">
                        <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                            <div>
                                <h3>{turma.nome}</h3>
                                <p className="text-sm text-gray-400">{turma.codigo} · {turma.ano_letivo} · {turma.turno}</p>
                            </div>
                            <span className="professor-pill">{turma.alunos.length} alunos</span>
                        </div>

                        {truthy(truthy(turma.alunos) && truthy(turma.disciplinas)) ? <> 
                        <div className="professor-table-wrapper">
                            <table className="w-full text-left">
                                <thead>
                                    <tr className="text-gray-500 text-xs uppercase tracking-wider">
                                        <th className="pb-4 font-medium">Aluno</th>
                                        <th className="pb-4 font-medium">Nota</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm">
                                    {turma.alunos.map((aluno, index37) => <Fragment key={aluno?.id ?? index37}>
                                    <tr className="border-t border-white/5">
                                        <td className="py-4">
                                            <span className="block font-bold text-white">{aluno.nome}</span>
                                            <span className="text-xs text-gray-500">{aluno.matricula}</span>
                                        </td>
                                        <td className="py-4">
                                            <MutationForm action={"/api/professor/notas/salvar"} method="post" className="professor-grade-form">
                                                <input type="hidden" name="turma_id" value={turma.id} />
                                                <input type="hidden" name="aluno_id" value={aluno.id} />
                                                <select name="disciplina_id" required>
                                                    {turma.disciplinas.map((disciplina, index38) => <Fragment key={disciplina?.id ?? index38}>
                                                    <option value={disciplina.id}>{disciplina.nome}</option>
                                                    </Fragment>)}
                                                </select>
                                                <input name="nota" type="number" min="0" max="10" step="0.01" placeholder="0-10" required />
                                                <input name="observacao" type="text" placeholder="Observação" />
                                                <button>Salvar nota</button>
                                            </MutationForm>
                                        </td>
                                    </tr>
                                    </Fragment>)}
                                </tbody>
                            </table>
                        </div>
                         </> : <> 
                        <p className="text-sm text-gray-400">Esta turma precisa ter alunos e disciplinas para lançar notas.</p>
                         </>}
                    </article>
                    </Fragment>)}</> : <>
                    <div className="professor-doc-block">
                        <h3>Nenhuma turma disponível</h3>
                        <p className="text-sm text-gray-400">Quando a administração associar turmas ao seu cadastro, o lançamento de notas aparecerá aqui.</p>
                    </div>
                    </>}
                </div>
            </div>

            <div className="glass-card professor-card rounded-[32px] p-8">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">Notas Lançadas</h2>
                    <span className="text-sm text-gray-400">Histórico recente</span>
                </div>

                <div className="professor-table-wrapper">
                <table className="w-full text-left">
                    <thead>
                        <tr className="text-gray-500 text-xs uppercase tracking-wider">
                            <th className="pb-4 font-medium">Aluno</th>
                            <th className="pb-4 font-medium">Turma</th>
                            <th className="pb-4 font-medium">Disciplina</th>
                            <th className="pb-4 font-medium">Nota</th>
                            <th className="pb-4 font-medium">Observação</th>
                            <th className="pb-4 font-medium">Data</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm">
                        {notas.length ? <>{notas.map((nota, index39) => <Fragment key={nota?.id ?? index39}>
                        <tr className="border-t border-white/5">
                            <td className="py-4 font-medium text-white">{nota.aluno}</td>
                            <td className="py-4 text-gray-400">{nota.turma}</td>
                            <td className="py-4 text-gray-400">{nota.disciplina}</td>
                            <td className="py-4 text-cyan-400 font-bold">{nota.nota}</td>
                            <td className="py-4 text-gray-400">{nota.observacao}</td>
                            <td className="py-4 text-gray-400">{nota.data}</td>
                        </tr>
                        </Fragment>)}</> : <>
                        <tr className="border-t border-white/5">
                            <td className="py-6 text-gray-400" colSpan="6">Nenhuma nota lançada até o momento.</td>
                        </tr>
                        </>}
                    </tbody>
                </table>
                </div>
            </div>
        </TabPanel>

        <TabPanel group="professor" value="documentos" as="section" className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_420px]">
            <div className="glass-card professor-card rounded-[32px] p-8">
                <h2 className="text-xl font-bold">Solicitações da Secretaria</h2>
                <p className="mt-1 text-sm text-gray-400">Anexe aqui os documentos pedidos pela secretaria.</p>

                {solicitacoes_documentos.length ? <>{solicitacoes_documentos.map((solicitacao, index40) => <Fragment key={solicitacao?.id ?? index40}>
                <article className="professor-doc-block">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                            <h3>{solicitacao.titulo}</h3>
                            <p className="text-sm text-gray-400">{solicitacao.mensagem}</p>
                            <span className="text-xs text-gray-500">{solicitacao.data}</span>
                        </div>
                        <strong className={`professor-request-status professor-request-status-${solicitacao.status}`}>{solicitacao.status_label}</strong>
                    </div>
                    {truthy(solicitacao.status !== "enviado") ? <> 
                    <MutationForm action={"/api/professor/documentos/upload"} method="post" encType="multipart/form-data" className="professor-doc-form mt-4">
                        <input type="hidden" name="solicitacao_id" value={solicitacao.id} />
                        <label>
                            <span>Arquivo</span>
                            <input name="arquivo" type="file" required />
                        </label>
                        <button>Enviar documento</button>
                    </MutationForm>
                     </> : <>  </>}
                </article>
                </Fragment>)}</> : <>
                <div className="professor-doc-block">
                    <h3>Nenhuma solicitação</h3>
                    <p className="text-sm text-gray-400">Quando a secretaria solicitar um documento, ele aparecerá aqui.</p>
                </div>
                </>}
            </div>

            <div className="glass-card professor-card rounded-[32px] p-8">
                <h2 className="text-xl font-bold">Documentos Enviados</h2>
                <p className="mt-1 text-sm text-gray-400">Histórico dos arquivos respondidos à secretaria.</p>

                <div className="mt-6 space-y-4">
                    {documentos.length ? <>{documentos.map((documento, index41) => <Fragment key={documento?.id ?? index41}>
                    <article className="professor-doc-item">
                        <div>
                            <h3>{documento.titulo}</h3>
                            <p>{documento.disciplina}</p>
                            <span>{documento.data}</span>
                        </div>
                        <a href={`/arquivos/download/${encodeURIComponent(documento.arquivo)}`}>Baixar</a>
                    </article>
                    </Fragment>)}</> : <>
                    <div className="professor-doc-item">
                        <div>
                            <h3>Nenhum documento enviado</h3>
                            <p>Os documentos enviados aparecerão aqui.</p>
                        </div>
                    </div>
                    </>}
                </div>
            </div>
        </TabPanel>
    </main>
    </>;
}
