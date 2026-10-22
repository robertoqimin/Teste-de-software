import React, { Fragment } from 'react';

import { AdminSidebar } from '../components/Navigation';
import { MutationForm } from '../components/MutationForm';

import { truthy } from '../utils';

export default function AdminComunicados({ data }) {
    const { comunicados = [], error = null } = data;
    return <>

    <AdminSidebar />

    <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
            <div>
                <h1 className="text-3xl font-bold">Comunicados</h1>
                <p className="text-gray-400">Envie recados institucionais para alunos, professores e responsáveis.</p>
            </div>
            <div className="flex items-center gap-4">
                <div className="text-right">
                    <p className="text-sm font-bold">Admin Secretaria</p>
                    <p className="text-[10px] text-cyan-400">Online agora</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 border-2 border-white/20"></div>
            </div>
        </header>

        <div className="comunicados-layout">
            <section className="glass-card comunicado-card rounded-[20px] p-10">
                <div className="mb-10 flex items-center gap-4">
                    <h2 className="text-2xl font-bold">Comunicado Geral</h2>
                </div>

                {truthy(error) ? <> 
                <p className="mb-6 rounded-xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">{error}</p>
                 </> : <>  </>}

                <MutationForm action="/api/admin/comunicados" method="post" className="space-y-9">
                    <label className="block">
                        <span className="mb-2 block text-sm font-bold text-slate-300">Título do Recado</span>
                        <input name="titulo" type="text" placeholder="Ex: Reunião de Pais e Mestres" className="comunicado-field" required />
                    </label>

                    <label className="block">
                        <span className="mb-2 block text-sm font-bold text-slate-300">Mensagem</span>
                        <textarea name="mensagem" rows="6" placeholder="Digite a mensagem oficial para envio imediato..." className="comunicado-field comunicado-textarea" required></textarea>
                    </label>

                    <div className="flex justify-end">
                        <button type="submit" className="comunicado-submit">
                            Disparar Comunicado

                        </button>
                    </div>
                </MutationForm>
            </section>

            <aside className="glass-card comunicados-enviados rounded-[20px] p-8">
                <h2 className="text-lg font-bold">Recados Enviados</h2>

                <div className="mt-7 space-y-4">
                    {comunicados.length ? <>{comunicados.map((comunicado, index3) => <Fragment key={comunicado?.id ?? index3}>
                    <article className="recado-card">
                        <div className="flex items-start justify-between gap-4">
                            <h3>{comunicado.titulo}</h3>
                            <span>{comunicado.created_at_label}</span>
                        </div>
                        <p>{comunicado.mensagem_resumo}</p>
                    </article>
                    </Fragment>)}</> : <>
                    <div className="recado-card">
                        <h3>Nenhum comunicado enviado</h3>
                        <p>Os recados criados aparecerão nesta lista.</p>
                    </div>
                    </>}
                </div>

                <button className="ver-todos-button">Ver todos os envios</button>
            </aside>
        </div>
    </main>

    
    </>;
}
