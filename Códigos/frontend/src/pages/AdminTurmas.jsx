import React, { Fragment } from 'react';

import { AdminSidebar } from '../components/Navigation';
import { MutationForm } from '../components/MutationForm';

import { truthy } from '../utils';

export default function AdminTurmas({ data }) {
    const { aluno_vinculos = [], alunos = [], disciplina_vinculos = [], error = null, professor_vinculos = [], professores = [], turmas = [] } = data;
    return <>

    <AdminSidebar />

    <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
            <div>
                <h1 className="text-3xl font-bold">Turmas</h1>
                <p className="text-gray-400">Cadastre turmas e associe alunos e professores.</p>
            </div>
            <div className="flex items-center gap-4">
                <div className="text-right">
                    <p className="text-sm font-bold">Admin Secretaria</p>
                    <p className="text-[10px] text-cyan-400">Online agora</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 border-2 border-white/20"></div>
            </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-[380px_minmax(0,1fr)] gap-8">
            <MutationForm action={"/api/admin/turmas"} method="post" className="glass-card turma-card rounded-[32px] p-8">
                <input type="hidden" name="action" value="create" />
                <h2 className="text-xl font-bold">Nova Turma</h2>
                <p className="mt-1 text-sm text-gray-400">Informe os dados principais da turma.</p>

                {truthy(error) ? <> 
                <div className="turma-alert">{error}</div>
                 </> : <>  </>}

                <label className="turma-field">
                    <span>Nome</span>
                    <input name="nome" type="text" placeholder="Ex: 1º Ano A" required />
                </label>

                <label className="turma-field">
                    <span>Código</span>
                    <input name="codigo" type="text" placeholder="Ex: 1A-2026" required />
                </label>

                <label className="turma-field">
                    <span>Ano letivo</span>
                    <input name="ano_letivo" type="number" min="2000" step="1" placeholder="Ex: 2026" required />
                </label>

                <label className="turma-field">
                    <span>Turno</span>
                    <select name="turno">
                        <option value="">Selecione o turno</option>
                        <option value="Matutino">Matutino</option>
                        <option value="Vespertino">Vespertino</option>
                        <option value="Noturno">Noturno</option>
                        <option value="Integral">Integral</option>
                    </select>
                </label>

                <button className="turma-submit">Cadastrar Turma</button>
            </MutationForm>

            <section className="glass-card turma-card rounded-[32px] p-8">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold">Turmas Cadastradas</h2>
                        <p className="text-sm text-gray-400">{turmas.length} registros encontrados</p>
                    </div>
                </div>

                <div className="turma-table-wrapper">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-gray-500 text-xs uppercase tracking-wider">
                                <th className="pb-4 font-medium">Nome</th>
                                <th className="pb-4 font-medium">Código</th>
                                <th className="pb-4 font-medium">Ano</th>
                                <th className="pb-4 font-medium text-right">Turno</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm">
                            {turmas.length ? <>{turmas.map((turma, index16) => <Fragment key={turma?.id ?? index16}>
                            <tr className="border-t border-white/5">
                                <td className="py-4 font-medium text-white">{turma.nome}</td>
                                <td className="py-4 text-cyan-400">{turma.codigo}</td>
                                <td className="py-4 text-gray-400">{turma.ano_letivo}</td>
                                <td className="py-4 text-right text-gray-400">{turma.turno}</td>
                            </tr>
                            </Fragment>)}</> : <>
                            <tr className="border-t border-white/5">
                                <td className="py-6 text-gray-400" colSpan="4">Nenhuma turma cadastrada.</td>
                            </tr>
                            </>}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>

        <section className="grid grid-cols-1 xl:grid-cols-2 gap-8 mt-8">
            <MutationForm action={"/api/admin/turmas"} method="post" className="glass-card turma-card rounded-[32px] p-8">
                <input type="hidden" name="action" value="associate_student" />
                <h2 className="text-xl font-bold">Associar Aluno</h2>
                <p className="mt-1 text-sm text-gray-400">Vincule um aluno a uma turma cadastrada.</p>

                <label className="turma-field">
                    <span>Aluno</span>
                    <select name="aluno_id" required>
                        <option value="">Selecione um aluno</option>
                        {alunos.map((aluno, index17) => <Fragment key={aluno?.id ?? index17}>
                        <option value={aluno.id}>{aluno.nome} - {aluno.matricula}</option>
                        </Fragment>)}
                    </select>
                </label>

                <label className="turma-field">
                    <span>Turma</span>
                    <select name="turma_id" required>
                        <option value="">Selecione uma turma</option>
                        {turmas.map((turma, index18) => <Fragment key={turma?.id ?? index18}>
                        <option value={turma.id}>{turma.nome} - {turma.codigo}</option>
                        </Fragment>)}
                    </select>
                </label>

                <button className="turma-submit">Associar Aluno</button>
            </MutationForm>

            <MutationForm action={"/api/admin/turmas"} method="post" className="glass-card turma-card rounded-[32px] p-8">
                <input type="hidden" name="action" value="associate_teacher" />
                <h2 className="text-xl font-bold">Associar Professor</h2>
                <p className="mt-1 text-sm text-gray-400">As disciplinas do professor serão vinculadas à turma automaticamente.</p>

                <label className="turma-field">
                    <span>Professor</span>
                    <select name="professor_id" required>
                        <option value="">Selecione um professor</option>
                        {professores.map((professor, index19) => <Fragment key={professor?.id ?? index19}>
                        <option value={professor.id}>{professor.nome} - {professor.disciplinas}</option>
                        </Fragment>)}
                    </select>
                </label>

                <label className="turma-field">
                    <span>Turma</span>
                    <select name="turma_id" required>
                        <option value="">Selecione uma turma</option>
                        {turmas.map((turma, index20) => <Fragment key={turma?.id ?? index20}>
                        <option value={turma.id}>{turma.nome} - {turma.codigo}</option>
                        </Fragment>)}
                    </select>
                </label>

                <button className="turma-submit">Associar Professor</button>
            </MutationForm>
        </section>

        <section className="grid grid-cols-1 xl:grid-cols-2 gap-8 mt-8">
            <div className="glass-card turma-card rounded-[32px] p-8">
                <h2 className="text-xl font-bold">Alunos por Turma</h2>
                <div className="turma-link-list">
                    {aluno_vinculos.length ? <>{aluno_vinculos.map((vinculo, index21) => <Fragment key={vinculo?.id ?? index21}>
                    <article className="turma-link-item">
                        <div>
                            <h3>{vinculo.aluno}</h3>
                            <p>{vinculo.matricula}</p>
                        </div>
                        <div className="text-right">
                            <strong>{vinculo.turma}</strong>
                            <span>{vinculo.codigo}</span>
                        </div>
                    </article>
                    </Fragment>)}</> : <>
                    <div className="turma-empty">Nenhum aluno associado ainda.</div>
                    </>}
                </div>
            </div>

            <div className="glass-card turma-card rounded-[32px] p-8">
                <h2 className="text-xl font-bold">Professores por Turma</h2>
                <div className="turma-link-list">
                    {professor_vinculos.length ? <>{professor_vinculos.map((vinculo, index22) => <Fragment key={vinculo?.id ?? index22}>
                    <article className="turma-link-item">
                        <div>
                            <h3>{vinculo.professor}</h3>
                            <p>{vinculo.disciplina}</p>
                        </div>
                        <div className="text-right">
                            <strong>{vinculo.turma}</strong>
                            <span>{vinculo.codigo}</span>
                        </div>
                    </article>
                    </Fragment>)}</> : <>
                    <div className="turma-empty">Nenhum professor associado ainda.</div>
                    </>}
                </div>
            </div>
        </section>

        <section className="mt-8">
            <div className="glass-card turma-card rounded-[32px] p-8">
                <h2 className="text-xl font-bold">Disciplinas puxadas dos Professores</h2>
                <div className="turma-link-list">
                    {disciplina_vinculos.length ? <>{disciplina_vinculos.map((vinculo, index23) => <Fragment key={vinculo?.id ?? index23}>
                    <article className="turma-link-item">
                        <div>
                            <h3>{vinculo.disciplina}</h3>
                            <p>{vinculo.disciplina_codigo}</p>
                        </div>
                        <div className="text-right">
                            <strong>{vinculo.turma}</strong>
                            <span>{vinculo.codigo}</span>
                        </div>
                    </article>
                    </Fragment>)}</> : <>
                    <div className="turma-empty">Nenhuma disciplina associada ainda.</div>
                    </>}
                </div>
            </div>
        </section>
    </main>

    
    </>;
}
