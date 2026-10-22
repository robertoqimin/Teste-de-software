import React, { Fragment } from 'react';

import { AdminSidebar } from '../components/Navigation';
import { MutationForm } from '../components/MutationForm';

import { truthy } from '../utils';

export default function AdminDisciplinas({ data }) {
    const { disciplinas = [], error = null, professor_vinculos = [], professores = [] } = data;
    return <>

    <AdminSidebar />

    <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
            <div>
                <h1 className="text-3xl font-bold">Disciplinas</h1>
                <p className="text-gray-400">Cadastre e acompanhe as disciplinas usadas em notas e documentos.</p>
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
            <MutationForm action={"/api/admin/disciplinas"} method="post" className="glass-card discipline-card rounded-[32px] p-8">
                <input type="hidden" name="action" value="create" />
                <h2 className="text-xl font-bold">Nova Disciplina</h2>
                <p className="mt-1 text-sm text-gray-400">Informe os dados principais da disciplina.</p>

                {truthy(error) ? <> 
                <div className="discipline-alert">{error}</div>
                 </> : <>  </>}

                <label className="discipline-field">
                    <span>Nome</span>
                    <input name="nome" type="text" placeholder="Ex: Matemática" required />
                </label>

                <label className="discipline-field">
                    <span>Código</span>
                    <input name="codigo" type="text" placeholder="Ex: MAT" required />
                </label>

                <label className="discipline-field">
                    <span>Carga horária</span>
                    <input name="carga_horaria" type="number" min="0" step="1" placeholder="Ex: 80" required />
                </label>

                <button className="discipline-submit">Cadastrar Disciplina</button>
            </MutationForm>

            <section className="glass-card discipline-card rounded-[32px] p-8">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold">Disciplinas Cadastradas</h2>
                        <p className="text-sm text-gray-400">{disciplinas.length} registros encontrados</p>
                    </div>
                </div>

                <div className="discipline-table-wrapper">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-gray-500 text-xs uppercase tracking-wider">
                                <th className="pb-4 font-medium">Nome</th>
                                <th className="pb-4 font-medium">Código</th>
                                <th className="pb-4 font-medium text-right">Carga Horária</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm">
                            {disciplinas.length ? <>{disciplinas.map((disciplina, index11) => <Fragment key={disciplina?.id ?? index11}>
                            <tr className="border-t border-white/5">
                                <td className="py-4 font-medium text-white">{disciplina.nome}</td>
                                <td className="py-4 text-cyan-400">{disciplina.codigo}</td>
                                <td className="py-4 text-right text-gray-400">{disciplina.carga_horaria}h</td>
                            </tr>
                            </Fragment>)}</> : <>
                            <tr className="border-t border-white/5">
                                <td className="py-6 text-gray-400" colSpan="3">Nenhuma disciplina cadastrada.</td>
                            </tr>
                            </>}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>

        <section className="grid grid-cols-1 xl:grid-cols-[380px_minmax(0,1fr)] gap-8 mt-8">
            <MutationForm action={"/api/admin/disciplinas"} method="post" className="glass-card discipline-card rounded-[32px] p-8">
                <input type="hidden" name="action" value="associate_teacher" />
                <h2 className="text-xl font-bold">Associar Professor</h2>
                <p className="mt-1 text-sm text-gray-400">Vincule um professor responsável à disciplina.</p>

                <label className="discipline-field">
                    <span>Professor</span>
                    <select name="professor_id" required>
                        <option value="">Selecione um professor</option>
                        {professores.map((professor, index12) => <Fragment key={professor?.id ?? index12}>
                        <option value={professor.id}>{professor.nome} - {professor.disciplina}</option>
                        </Fragment>)}
                    </select>
                </label>

                <label className="discipline-field">
                    <span>Disciplina</span>
                    <select name="disciplina_id" required>
                        <option value="">Selecione uma disciplina</option>
                        {disciplinas.map((disciplina, index13) => <Fragment key={disciplina?.id ?? index13}>
                        <option value={disciplina.id}>{disciplina.nome} - {disciplina.codigo}</option>
                        </Fragment>)}
                    </select>
                </label>

                <button className="discipline-submit">Associar Professor</button>
            </MutationForm>

            <div className="glass-card discipline-card rounded-[32px] p-8">
                <h2 className="text-xl font-bold">Professores por Disciplina</h2>
                <div className="discipline-link-list">
                    {professor_vinculos.length ? <>{professor_vinculos.map((vinculo, index14) => <Fragment key={vinculo?.id ?? index14}>
                    <article className="discipline-link-item">
                        <div>
                            <h3>{vinculo.professor}</h3>
                            <p>{vinculo.data}</p>
                        </div>
                        <div className="text-right">
                            <strong>{vinculo.disciplina}</strong>
                            <span>{vinculo.codigo}</span>
                        </div>
                    </article>
                    </Fragment>)}</> : <>
                    <div className="discipline-empty">Nenhum professor associado ainda.</div>
                    </>}
                </div>
            </div>
        </section>
    </main>

    
    </>;
}
